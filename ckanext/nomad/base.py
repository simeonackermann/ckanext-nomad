from ckanext.harvest.harvesters import HarvesterBase

import requests
from requests.exceptions import HTTPError, RequestException

import datetime
from urllib3.contrib import pyopenssl
import urllib

from ckan import model
from ckan.logic import ValidationError, NotFound, get_action
from ckan.lib.helpers import json
from ckanext.harvest.model import HarvestObject

import logging
log = logging.getLogger(__name__)

class MockRequest(object):
    data = None

    def __init__(self, data):
        self.data = data


    def json(self):
        return self.data


mock_noResults = MockRequest({
    "results": []
})

mock_10Results = MockRequest({
    "results": [
        { "pid": '1', "formula": "AbC" },
        { "pid": '2', "formula": "AbC1" },
        { "pid": '3', "formula": "AbC2" },
        { "pid": '4', "formula": "AbCD" },
        { "pid": '5', "formula": "AbCD1" },
        { "pid": '6', "formula": "EfG" },
        { "pid": '7', "formula": "HiJ" },
        { "pid": '8', "formula": "HiJk1" },
        { "pid": '9', "formula": "HiJk2" },
        { "pid": '10' },
    ]
})

class NOMADHarvester(HarvesterBase):

    def modify_package_dict(self, package_dict, harvest_object):
        '''
            Allows custom harvesters to modify the package dict before
            creating or updating the actual package.
        '''
        return package_dict

    def _search_for_datasets(self, remote_ckan_base_url, fq_terms=None):
        log.debug('In NOMADJSONHarvester _search_for_datasets')

        params = {'per_page': 3, 'page': 1, 'order_by': 'pid', 'order': 1}
        pkg_dicts = []
        previous_content = None

        if fq_terms:
            params.update(fq_terms)

        while True:
            url = remote_ckan_base_url + '?' + urllib.urlencode(params)
            log.debug("NOMAD search URL: %s", url)

            try:
                content = self._get_content(url)
            except Exception as e:
                raise Exception('Error sending request to NOMAD. Url: %s Error: %s' % (url, e))

            if previous_content and content == previous_content:
                raise Exception('The paging doesn\'t seem to work. URL: %s' % url)

            try:
                response_dict = content.json()
                # response_dict = json.loads(content)
            except Exception:
                raise Exception('Response from remote NOMAD was not JSON: %r' % content)

            try:
                pkg_dicts_page = response_dict.get('results', [])
            except Exception:
                raise Exception('Response JSON did not contain results: %r' % response_dict)

            if len(pkg_dicts_page) == 0:
                # no more datasets found ...
                log.debug('No more datasets in remote NOMAD found. Finishing search: %s', url)
                break

            # TODO: may weed out any datasets those are changing while we page ... ?
            # used from ckanharvester:
            #   ids_in_page = set(p['pid'] for p in pkg_dicts_page)

            pkg_dicts.extend(pkg_dicts_page)

            params['page'] += 1

            # TODO remove dev finihsing after 10 results
            if (len(pkg_dicts) + params['per_page']) > 10:
                # finishing after 10 results!
                break

        return pkg_dicts

    def _get_content(self, url):
        '''
        - do http request to fetch content from remote host
        '''

        log.debug("NOMADHavrester in _get_content (%s)", url)

        # raise Exception("This is my error message. ...")
        # return None
        # return mock_10Results

        headers = {}
        # TODO allow apiKey x-Token auth
        # api_key = self.config.get('api_key')
        # if api_key:
        #     headers['Authorization'] = api_key

        # pyopenssl.inject_into_urllib3()

        try:
            http_request = requests.get(url, headers=headers)
        except Exception as e:
            raise Exception(e)

        #     raise ContentFetchError('HTTP error: %s %s' % (e.response.status_code, e.request.url))
        # except RequestException as e:
        #     raise ContentFetchError('Request error: %s' % e)
        # except Exception as e:
        #     raise ContentFetchError('HTTP general exception: %s' % e)
        # return http_request.json()
        return http_request
