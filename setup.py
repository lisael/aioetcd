# -*- coding: utf-8 -*-
"""Python packaging."""
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

NAME = 'aioetcd'
DESCRIPTION = """Coroutine based etcd client"""
try:
    README = open(os.path.join(here, 'README.md')).read()
except:
    README = ""
# VERSION = open(os.path.join(here, 'VERSION')).read().strip()
VERSION = '0.1'
AUTHOR = u'lisael'
EMAIL = u'lisael@lisael.org'
LICENSE = u'AGPL'
URL = u'https://github.com/lisael/aioetcd'
CLASSIFIERS = ['Development Status :: 3 - Alpha',
               'Programming Language :: Python :: 3.4',
               'License :: Other/Proprietary License']
KEYWORDS = ['asyncio', 'etcd']
PACKAGES = [
    "aioetcd",
]

NAMESPACE_PACKAGES = []
REQUIREMENTS = [
    "aiohttp",
]

SCRIPTS = [
]


if __name__ == '__main__':  # Don't run setup() when we import this module.
    setup(name=NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=README,
          classifiers=CLASSIFIERS,
          keywords=' '.join(KEYWORDS),
          author=AUTHOR,
          author_email=EMAIL,
          url=URL,
          license=LICENSE,
          packages=PACKAGES,
          namespace_packages=NAMESPACE_PACKAGES,
          include_package_data=True,
          zip_safe=False,
          scripts=SCRIPTS,
          install_requires=REQUIREMENTS,
    )
