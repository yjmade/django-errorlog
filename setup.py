#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
# import sys

# if 'bdist_wheel' in sys.argv:
from pypandoc import convert
long_description = convert('README.md', 'rst')
VERSION = "0.1.0"
print find_packages()
setup(
    name='django-errorlog',
    version=VERSION,
    description='Django reuseable app to collect the unexpcted exception then generate comprehansive report just like what you get in debug mode and store in database',
    url="https://github.com/yjmade/django-errorlog",
    long_description=long_description,
    author='Jay Young(yjmade)',
    author_email='dev@yjmade.net',
    packages=find_packages(),
    install_requires=["django>1.9"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    license='MIT',
    keywords='django error log report',

)
