#!/usr/bin/env python
from setuptools import setup, find_packages
from sys import platform
require = ['argparse']
if platform.startswith('linux'):
	require.append('readline')
else:
	require.append('pyreadline')
setup(name='codebake',
		version='1.1',
		description='Utility for quickly minifying and obfuscating JavaScript',
		url='http://github.com/sparkida/augment',
		author='Nicholas Riley',
		author_email='nick@sparkida.com',
		license='MIT',
		scripts=['bake'],
		platforms='Linux',
		install_requires=require,
		packages=find_packages())

