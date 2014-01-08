#!/usr/bin/env python
from distutils.core import setup
import sys, os
setup(name='codebake',
		version='1.0',
		description='Utility for quickly minifying and obfuscating JavaScript',
		url='http://github.com/sparkida/augment',
		author='Nicholas Riley',
		author_email='nick@sparkida.com',
		license='MIT',
		scripts=['bake'],
		platforms='Linux',
		packages=['codebake'])

