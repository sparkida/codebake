#!/usr/bin/python

import cProfile
import re
import os
import sys
from pstats import Stats
from numpy import array
from cli import Console
from glob import glob
from time import clock
from __init__ import Bind
sep = os.path.sep

def build(usebypass = False, filepath = ''):
	'''
	build - runs main profiler
	params::
		bypass = False : use when iterating
	'''
	#if no args
	if not usebypass:
		global bypass, testlist, filelist, profile, logfile, codebake, profiledir, testdir, initpath
		if len(sys.argv) == 0:
			print('Error: Should not be imported!')
			return 1	
		#check init path
		initpath = os.getcwd()
		#make sure we are executing this script directly
		start = re.search(r'(%scodebake)\1' % (sep,), initpath)
		if start == None:
			exit('Error: Could not initialize...\nPlease run from within Codebake directory')
		testdir = '%s%stests' % (initpath, sep)
		if not os.path.isdir(testdir):
			print('Error: Could not establish Codebake tests directory.')
			return 1
		#check profiler directory
		profiledir = '%s%sprofiles' % (initpath, sep)
		logfile = '%s%slog' % (profiledir, sep)
		#make profile log directory
		if not os.path.isdir(profiledir):
			os.makedirs(profiledir)
		#get test files
		testlist = glob('%s%s*.js' % (testdir, sep))
		filelist = ['.'.join(os.path.basename(x).split('.')[:-1]) for x in testlist]
		arglength = len(sys.argv)
		#resolve filepath
		if arglength < 2:
			filepath = setopts()
		else:
			#expand path
			filepath = '%s%s%s' % (testdir, sep, sys.argv[1])
			if filepath not in testlist:
				print('Error: Invalid file...\nPlease use files in tests directory')
				filepath = setopts()
	bypass = usebypass
	fn = os.path.basename(filepath)
	codebake = '%s%s__init__.py' % (initpath, sep)
	fnbase = '.'.join(fn.split('.')[:-1])
	profile = '%s%s%s.profile' % (profiledir, sep, fnbase)
	#end bypass
	#check if we chould use cache
	#retrieve from cache
	return setprofile(filepath, bypass)


def setprofile(filepath, bypass):
	cache = setcache(filepath)
	sys.argv[:] = ['__init__', '-df', filepath]
	start = float(clock())
	#temporarily swap stdout
	errormsg = 'Error: An unkown error has occured trying to execute cProfile\n%s::%s'
	#create log file
	start = float(clock())
	base = os.path.basename(filepath)
	expand = '%s::%0.7f\n'
	if not cache.used:
		mtime = os.path.getmtime(filepath)
		if writeprofile():
			with open(logfile, 'a') as log:
				if cache.new or cache.add:
					log.write(expand % (base, mtime))
				else:
					lines = log.readlines()
					lines[cache.updateIndex] = expand % (base, mtime)
					log.writelines(lines)
		else:
			if os.path.isfile(profile):
				os.unlink(profile)
			print(errormsg % (base, '101'))
			return 1
	if not bypass:
		showstats(float(clock()) - start, cache.used)
	return 0


def writeprofile():
	sort = 'totaltime'
	success = False
	back = sys.stdout
	try:
		print('\nInitializing profile...')
		with open(os.devnull, 'w') as so:
			sys.stdout = so
			cProfile.run('execfile(%r)' % (codebake,), profile, sort)
			success = True
	except:
		pass
	#cache non bypass mode
	sys.stdout = back
	return success


def showstats(time, fromcache = False):
	outstring = ['----------------------------',
			'Done! Profile completed in %.02f seconds' % time,
			'File written to %s' % profile
			]
	if fromcache:
		outstring[2] = '(from cache)'
	stats = Stats(profile)
	stats.sort_stats('time')
	stats.print_stats()
	print('\n'.join(outstring))


def setcache(filepath):
	start = float(clock())
	count = -1
	update = False
	updateIndex = None
	new = True
	add = True
	used = False
	base = os.path.basename(filepath)
	origmtime = os.path.getmtime(filepath)
	if os.path.isfile(logfile):
		new = False
		with open(logfile, 'r') as log:
			lines = log.readlines()
			for n in lines:
				count += 1
				(fn, mtime) = n.split('::')
				mtime = float(mtime[:-1])
				#has the file been profiled?
				if fn == base:
					add = False
					#does the file need updating
					if mtime == origmtime:
						#showstats(float(clock()) - start)
						used = True
					else:
						update = True
						updateIndex = count
					break
	cache = {
			'add': add,
			'new': new,
			'update': update,
			'updateIndex': updateIndex,
			'used': used
			}
	return Bind(cache)
	#end open logfile


def setopts(show = True):
	#get from selection
	if show:
		listfiles()
	select = getselect()
	if select == 0:
		errors = ''
		count = 0
		for d in os.listdir(profiledir):
			d = '%s/%s' % (profiledir, d)
			if not os.path.islink(d):
				print('deleting: %s' % d)
				os.unlink(d)
		for n in testlist:
			if build(True, n) == 1:
				errors += '%s\n' % n
				continue
			count += 1
		print('Profiled %s of %s tests' % (count, len(testlist)))
		print('0 errors occured' if errors == '' else 'Errors occured in the following files:\n%s' % errors)
		sys.exit(0)
	try:
		#get user selection
		return testlist[select - 1]
	except:
		return setopts(False)


def listfiles():
	out = 'Select target to profile:\n0: REBUILD_ALL\n'
	count = 0
	gap = '\n'
	for n in filelist:
		count += 1
		out += '%d: %s%s' % (count, n, gap)
	#list files
	print(out)


#selection loop
def getselect():
	select = int(Console().raw_input('number > '))
	if select == None:
		return getselect()
	return select

#die, error
def exit(msg):
	print(msg)
	sys.exit(1)


if "__main__" == __name__:
	sys.exit(build())


