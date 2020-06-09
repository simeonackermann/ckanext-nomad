=============
ckanext-nomad
=============

Harvester for [NOMAD Respository API](https://repository.nomad-coe.eu/). Adds the ability to use NOMAD as harvester source type.

This extension is in a very early state to survey the feasibility of the NOMAD harvesting function.

------------
Requirements
------------

Requires the [ckanext-harvester](https://github.com/ckan/ckanext-harvest) extension.

------------
Installation
------------

Install ckanext-harvester first.

To install ckanext-nomad:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-nomad Python package into your virtual environment::

     pip install -e git+https://github.com/simeonackermann/ckanext-nomad.git#egg=ckanext-nomad

3. Add ``nomad`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN


-----
Usage
-----

Run the [ckanext-harvest](https://github.com/ckan/ckanext-harvest#configuration) installation and configuration.

Add a new NOMAD Harvester source under

    http://{ckan-instance-host}/harvest


Running the harvest jobs see https://github.com/ckan/ckanext-harvest#running-the-harvest-jobs . Eg. to run tests:

    (pyenv) $ ckan-paster --plugin=ckanext-harvest harvester run_test {harvest-id} -c $CKAN_CONFIG/production.ini

