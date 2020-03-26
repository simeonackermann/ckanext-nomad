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


---------------------------------
Registering ckanext-nomad on PyPI
---------------------------------

ckanext-nomad should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-nomad. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-nomad
----------------------------------------

ckanext-nomad is availabe on PyPI as https://pypi.python.org/pypi/ckanext-nomad.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
