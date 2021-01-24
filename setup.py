#!/usr/bin/env python
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import smmap

if os.path.exists("README.md"):
    long_description = open('README.md', "r", encoding="utf-8").read().replace('\r\n', '\n')
else:
    long_description = "See https://github.com/gitpython-developers/smmap"

setup(
    name="smmap",
    version=smmap.__version__,
    description="A pure Python implementation of a sliding window memory map manager",
    author=smmap.__author__,
    author_email=smmap.__contact__,
    url=smmap.__homepage__,
    platforms=["any"],
    license="BSD",
    packages=find_packages(),
    zip_safe=True,
    python_requires=">=3.4",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    tests_require=('nose', 'nosexcover'),
    test_suite='nose.collector'
)
