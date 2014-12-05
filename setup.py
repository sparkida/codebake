#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Codebake
Clean CSS, HTML, and JavaScript Files
v 1.4.0
Author: Nicholas Riley
"""

from os import path,sys
from setuptools import setup
require = ['argparse','readline','twisted']
if sys == 'nt':
    require.append('pyreadline')


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

#from sys import platforms
setup(name='Codebake',
        version='1.4.0',
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

