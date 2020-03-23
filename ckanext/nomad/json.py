# import ckan.plugins as plugins
# import ckan.plugins.toolkit as toolkit

import requests
from requests.exceptions import HTTPError, RequestException

import datetime
from urllib3.contrib import pyopenssl
import urllib

from ckan import model
from ckan.logic import ValidationError, NotFound, get_action
from ckan.lib.helpers import json
from ckanext.harvest.model import HarvestObject

from ckanext.nomad.base import NOMADHarvester

import logging
log = logging.getLogger(__name__)

# class NomadPlugin(plugins.SingletonPlugin):
#     plugins.implements(plugins.IConfigurer)

#     # IConfigurer

#     def update_config(self, config_):
#         toolkit.add_template_directory(config_, 'templates')
#         toolkit.add_public_directory(config_, 'public')
#         toolkit.add_resource('fanstatic', 'nomad')



class NOMADJSONHarvester(NOMADHarvester):

    def info(self):
        return {
            'name': 'nomad',
            'title': 'NOMAD Harvester (simple)',
            'description': 'Damns simple harvester for datasets from NOMAD Repo API'
        }

    def validate_config(self, config):
        '''

        [optional]

        Harvesters can provide this method to validate the configuration
        entered in the form. It should return a single string, which will be
        stored in the database.  Exceptions raised will be shown in the form's
        error messages.

        :param harvest_object_id: Config string coming from the form
        :returns: A string with the validated configuration options
        '''

    def get_original_url(self, harvest_object_id):
        '''

        [optional]

        This optional but very recommended method allows harvesters to return
        the URL to the original remote document, given a Harvest Object id.
        Note that getting the harvest object you have access to its guid as
        well as the object source, which has the URL.
        This URL will be used on error reports to help publishers link to the
        original document that has the errors. If this method is not provided
        or no URL is returned, only a link to the local copy of the remote
        document will be shown.

        Examples:
            * For a CKAN record: http://{ckan-instance}/api/rest/{guid}
            * For a WAF record: http://{waf-root}/{file-name}
            * For a CSW record: http://{csw-server}/?Request=GetElementById&Id={guid}&...

        :param harvest_object_id: HarvestObject id
        :returns: A string with the URL to the original document
        '''

    def gather_stage(self, harvest_job):
        '''
        The gather stage will receive a HarvestJob object and will be
        responsible for:
            - gathering all the necessary objects to fetch on a later.
            stage (e.g. for a CSW server, perform a GetRecords request)
            - creating the necessary HarvestObjects in the database, specifying
            the guid and a reference to its job. The HarvestObjects need a
            reference date with the last modified date for the resource, this
            may need to be set in a different stage depending on the type of
            source.
            - creating and storing any suitable HarvestGatherErrors that may
            occur.
            - returning a list with all the ids of the created HarvestObjects.
            - to abort the harvest, create a HarvestGatherError and raise an
            exception. Any created HarvestObjects will be deleted.

        :param harvest_job: HarvestJob object
        :returns: A list of HarvestObject ids
        '''
        log.debug('In NOMADJSONHarvester gather_stage (%s)', harvest_job.source.url)

        # TODO may use config
        # eg. add some filter (organizations, groups, ...) -> do we have such in nomad?!
        if harvest_job.source.config:
            log.debug('TODO: May use harvest config: %s', harvest_job.source.config)
        # self._set_config(harvest_job.source.config)

        # Get source URL
        remote_nomad_base_url = harvest_job.source.url.rstrip('/')

        pkg_dicts = None
        fq_terms = {}

        last_error_free_job = self.last_error_free_job(harvest_job)

        # TODO
        # may use the last error free job gathered time as new last edit time
        if(last_error_free_job):
            last_time = last_error_free_job.gather_started
            get_changes_since = \
                (last_time - datetime.timedelta(hours=1)).isoformat()

            log.info('Searching for datasets modified since: %s UTC', get_changes_since)
            fq_terms.update({'from_time': get_changes_since})

        # search for packages
        try:
            pkg_dicts = self._search_for_datasets(remote_nomad_base_url, fq_terms)
        except Exception as e:
            log.info("Searching for datasets gave an error: %s", e)
            return None

        if not pkg_dicts:
            log.info('No datasets found at NOMAD: %s', harvest_job)
            return []

        object_ids = []

        # basically create package dict
            # package_ids = set()

        for pkg_dict in pkg_dicts:
            try:
                if not pkg_dict.get('pid'):
                    # TODO create pid from another property?!
                    log.debug("Could not get a unique identifier for dataset: %s. Ignore dataset.", pkg_dict)
                    continue
                guid=pkg_dict['pid']
                pkg_dict['id'] = guid

                log.debug("Creating HarvestObject for %s", guid)
                obj = HarvestObject(guid=guid, job=harvest_job, content=json.dumps(pkg_dict))
                obj.save()
                object_ids.append(obj.id)

            except Exception as e:
                log.info("Gather gave an error: %s", e)
                # return None

        print("Results: %s:" % len(object_ids))
        # print("Results (%s): %s" % (len(pkg_dicts), pkg_dicts))

        return object_ids


    def fetch_stage(self, harvest_object):
        # Nothing to do here - we got the package dict in the search in the
        # gather stage
        return True

    def import_stage(self, harvest_object):
        '''
        The import stage will receive a HarvestObject object and will be
        responsible for:
            - performing any necessary action with the fetched object (e.g.y
            create, update or delete a CKAN package).
            Note: if this stage creates or updates a package, a reference
            to the package should be added to the HarvestObject.
            - setting the HarvestObject.package (if there is one)
            - setting the HarvestObject.current for this harvest:
            - True if successfully created/updated
            - False if successfully deleted
            - setting HarvestObject.current to False for previous harvest
            objects of this harvest source if the action was successful.
            - creating and storing any suitable HarvestObjectErrors that may
            occur.
            - creating the HarvestObject - Package relation (if necessary)
            - returning True if the action was done, "unchanged" if the object
            didn't need harvesting after all or False if there were errors.

        NB You can run this stage repeatedly using 'paster harvest import'.

        :param harvest_object: HarvestObject object
        :returns: True if the action was done, "unchanged" if the object didn't
                need harvesting after all or False if there were errors.
        '''
        log.debug('In NOMADJSONHarvester import_stage')

        if not harvest_object:
            log.error("No harvest object received")
            return False

        if harvest_object.content is None:
            log.info("Empty content for harvest object: %s", harvest_object.id)
            return False

        try:
            # package_dict = harvest_object.content
            package_dict = json.loads(harvest_object.content)
        except Exception as e:
            log.error("Could not parse content for harvest object: %s", harvest_object.id)
            return False

        package_dict["metadata_modified"] = package_dict.get('last_processing', None)

        base_context = {'model': model, 'session': model.Session,
                        'user': self._get_user_name()}

        # Local harvest source organization
        # source_dataset = model.Package.get(harvest_job.source.id)
        source_dataset = get_action('package_show')(base_context.copy(), {'id': harvest_object.source.id})

        # # pkg_dict["owner_org"] = source_dataset.owner_org
        package_dict["owner_org"] = source_dataset.get('owner_org')

        package_dict["name"] = package_dict.get('formula', package_dict.get('id'))
        package_dict["title"] = package_dict.get('name')

        package_dict["tags"] = package_dict.get('tags', [])
        package_dict["extras"] = package_dict.get('extras', [])
        package_dict['extras'].append({'key': 'calc_hash', 'value': package_dict.get('calc_hash', None)})

        package_dict['extras'].append({'key': 'FOO', 'value': package_dict.get('BAR', None)})

        if package_dict.get('mainfile'):
            package_dict['extras'].append({'key': 'mainfile', 'value': package_dict.get('mainfile')})

        if package_dict.get('formula'):
            package_dict['extras'].append({'key': 'formula', 'value': package_dict.get('formula')})

        # allow custom harvesters to modify package
        package_dict = self.modify_package_dict(package_dict, harvest_object)

        # log.debug('harvest_object: %s', package_dict)
        # return False

        return self._create_or_update_package(
            package_dict, harvest_object, package_dict_form='package_show'
        )
        # return True


