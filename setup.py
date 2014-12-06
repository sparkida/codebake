#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Codebake
Clean CSS, HTML, and JavaScript Files
Author: Nicholas Riley
"""

from os import path,sys
from setuptools import setup
require = ['argparse','readline','twisted']
if sys == 'nt':
    require.append('pyreadline')

def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

#set version
modulePath = path.join(path.dirname(path.realpath(__file__)), 'codebake/oven.py')
with open(modulePath, 'a+') as baker:
    lineNumber = 0
    lines = baker.readlines()
    while True:
        line = lines[lineNumber]
        words = line.strip().split()
        try:
            if '__version__' == words[0]:
                __version__ = words[2]
                break
        except IndexError:
            pass
        lineNumber += 1

#from sys import platforms
setup(name='Codebake',
        version=__version__,
        description='Utility to quickly minify source and inline JavaScript and CSS',
        url='https://github.com/sparkida/codebake',
        author='Nick Riley',
        author_email='nick@sparkida.com',
        license='MIT',
        long_description=read('README.md'),
        entry_points={'console_scripts': ['bake = Codebake.oven:Codebake']},
        install_requires=require,
        py_modules=['bake'],
        packages=['Codebake'],
        package_dir={'Codebake': 'codebake'},
        package_data={'Codebake': ['templates/*.html']})

