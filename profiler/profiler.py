"""
Codebake
Clean CSS, HTML, and JavaScript Files
v1.1
Author: Nicholas Riley
"""

import os,sys
from timeit import Timer

class BaseProfile(object):

	def __init__(self):
		stat = Timer(
				"call(['python', './codebake', '-df', 'tests/jquery.js'])",
				setup='from subprocess import call'
				).repeat(repeat=3, number=12)
		print(stat)

