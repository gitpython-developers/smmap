#!/usr/bin/env python
import os
import codecs
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import smmap

if os.path.exists("README.rst"):
    long_description = codecs.open('README.rst', "r", "utf-8").read()
else:
    long_description = "See http://github.com/nvie/smmap/tree/master"

setup(
    name="smmap",
    version=smmap.__version__,
    description="A pure git implementation of a sliding window memory map manager",
    author=smmap.__author__,
    author_email=smmap.__contact__,
    url=smmap.__homepage__,
    platforms=["any"],
    license="BSD",
    packages=find_packages(),
    zip_safe=True,
    classifiers=[
        # Picked from
        #    http://pypi.python.org/pypi?:action=list_classifiers
        #"Development Status :: 1 - Planning",
        #"Development Status :: 2 - Pre-Alpha",
        #"Development Status :: 3 - Alpha",
        "Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        #"Development Status :: 7 - Inactive",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
    ],
    long_description=long_description,
)
