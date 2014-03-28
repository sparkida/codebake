#!/usr/bin/env python
"""
Codebake
Clean CSS, HTML, and JavaScript Files
v1.1
Author: Nicholas Riley
"""

from os import path
from setuptools import setup
from sys import platform
require = ['argparse']
if platform.startswith('linux'):
	require.append('readline')
else:
	require.append('pyreadline')


def read(fname):
	return open(path.join(path.dirname(__file__), fname)).read()

#from sys import platforms
setup(name='Codebake',
		version='1.21',
		description='Utility for quickly minifying and obfuscating JavaScript',
		url='https://github.com/sparkida/codebake',
		author='Nicholas Riley',
		author_email='nick@sparkida.com',
		license='MIT',
		long_description=read('README.md'),
		entry_points={'console_scripts': ['bake = Codebake.oven:Codebake']},
		install_requires=require,
		py_modules=['bake'],
		packages=['Codebake'],
		package_dir={'Codebake':'codebake'})

