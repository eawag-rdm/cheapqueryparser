from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cheapqueryparser',
    version='1.0.0',
    description=('A simple parser for Lucene/Solr querystrings intended to be '
                 'used by CKAN extensions that implement IPackageController.be'
                 'fore_search'),
    long_description=long_description,
    url='https://github.com/eawag-rdm/cheapqueryparser',
    author='Harald von Waldow',
    author_email='harald.vonwaldow@eawag.ch',
    license='GNU Affero General Public License v3.0',

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3.0',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='Lucene query parsing CKAN',
    packages=['cheapqueryparser']
)
