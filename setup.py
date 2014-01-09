#!/usr/bin/env python
from setuptools import setup, find_packages
setup(name='codebake',
		version='1.0',
		description='Utility for quickly minifying and obfuscating JavaScript',
		url='http://github.com/sparkida/augment',
		author='Nicholas Riley',
		author_email='nick@sparkida.com',
		license='MIT',
		scripts=['bake'],
		platforms='Linux',
		install_requires=['argparse','readline'],
		packages=find_packages())

