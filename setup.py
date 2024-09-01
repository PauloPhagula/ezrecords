#!/usr/bin/env python
# coding: utf-8
"""
Setup script for package.
"""
from __future__ import unicode_literals, print_function
import os
import sys
import codecs
from email.utils import parseaddr
from setuptools import setup, find_packages

import ezrecords

if sys.argv[-1] == 'publish':
    os.system('python setup.py register')
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload --universal')
    sys.exit()

def file_get_contents(filename):
    """Reads an entire file into a string."""
    assert os.path.exists(filename) and os.path.isfile(filename), 'invalid filename: ' + filename
    return codecs.open(filename, 'r', 'utf-8').read()

SETUP_DIR = os.path.abspath(os.path.dirname(__file__))
AUTHOR, AUTHOR_EMAIL = parseaddr(ezrecords.__author__)
LONG_DESCRIPTION = '\n'.join([file_get_contents('README.rst'), file_get_contents('CHANGELOG.md')])

setup(
    name='ezrecords',
    version=ezrecords.__version__,
    description='SQL for the enhanced.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    url='https://github.com/dareenzo/ezrecords',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license='MIT',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Database',
        'Topic :: Utilities'
    ),
    keywords=('database', 'db', 'helper', 'utility', 'sql'),
    packages=find_packages(exclude=['tests']),
    install_requires=['tablib', 'docopt', 'munch', 'psycopg2', 'PyMySQL'],
    platforms='any',
    entry_points={
        'console_scripts': ['ezrecords=ezrecords.cli:cli']
    },
    include_package_data=True,
    zip_safe=False
)
