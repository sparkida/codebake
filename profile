#!/usr/bin/env python

import cProfile
import re
import os
import sys
from os.path import sep
from pstats import Stats
from numpy import array
from codebake.cli import Console
from glob import glob
from time import clock

        
class Bind(object):
    
    def __init__(self, dct):
        self.__dict__.update(dct)

    def get(self, index):
        try:
            return self.__dict__[index]
        except:
            return False


def build(usebypass = False, filepath = ''):
    '''
    build - runs main profiler
    params::
        bypass = False : use when iterating
    '''
    #if no args
    if not usebypass:
        global bypass, testlist, filelist, profile, logfile, codebake, profiledir, testdir, initpath, console
        console = Console()
        if len(sys.argv) == 0:
            error('Should not be imported!')
            return 1    
        #check init path
        initpath = os.getcwd()
        testdir = os.path.join(initpath, 'tests')
        if not os.path.isdir(testdir):
            error('Could not establish Codebake tests directory.')
            return 1
        #check profiler directory
        profiledir = os.path.join(initpath, 'profiles')
        logfile = os.path.join(profiledir, 'log')
        checkcache()
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
            filepath = '%s%s%s' % (testdir, sep, sys.argv[0])
            if filepath not in testlist:
                error('Invalid file...\nPlease use files in tests directory')
                filepath = setopts()
    bypass = usebypass
    fn = os.path.basename(filepath)
    fnbase = '.'.join(fn.split('.')[:-1])
    profile = os.path.join(profiledir, '%s.profile' % fnbase)
    codebake = os.path.join(initpath, 'codebake', 'profile.py')
    sys.path.insert(0, [os.path.join(initpath, 'codebake')])
    #end bypass
    #check if we chould use cache
    #retrieve from cache
    return setprofile(filepath, bypass)

def error(msg):
    print('\033[0;40mError: %s\033[0;m' % msg) 

def purgecache():
    for d in os.listdir(profiledir):
        d = '%s/%s' % (profiledir, d)
        print('\033[0;31mdeleting:\033[0;m \033[0;30m%s\033[0;m' % d)
        os.unlink(d)

def checkcache():
    if os.path.isfile(logfile):
        logmtime = os.path.getmtime(logfile)
        for n in glob('%s%s*.py' % (initpath, sep)):
            #if a file has been updated, purge cache
            if os.path.getmtime(n) >= logmtime:
                print('\033[0;35mCodebake updated! -- purging cache\033[0;m')
                purgecache()
                break
            
def setprofile(filepath, bypass):
    cache = setcache(filepath)
    sys.argv[:] = ['__init__', '-df', filepath]
    start = float(clock())
    #temporarily swap stdout
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
            error('An error has occured while trying to bake %s' % base)
            if not bypass:
                requestmod([base])
            return 1
    if not bypass:
        showstats(float(clock()) - start, cache.used)
    return 0


def requestmod(mods):
    import subprocess
    for n in mods:
        base = os.path.basename(n)
        answer = str(console.raw_input('Run test on %s module? [y/n]>' % base))
        if answer == '':
            pass
        elif re.search(r'y(es)?', answer, re.IGNORECASE).group() != None:
            subprocess.call('python ~/codebake/codebake -df tests/%s' % base, shell=True)


def writeprofile():
    sort = 'totaltime'
    success = False
    cProfile.run('execfile(%r)' % (codebake,), profile, sort)
    back = sys.stdout
    try:
        print('\n\033[0;30mInitializing profile...\033[0;m')
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
        purgecache()
        for n in testlist:
            if build(True, n) == 1:
                errors += '%s\n' % n
                continue
            count += 1
        print('Profiled \033[0;33m%s\033[0;m of \033[0;32m%s\033[0;m tests.' % (count, len(testlist)))
        if errors == '':
            print('\033[0;32m0 errors occured\033[0;m')
        else: 
            error('Errors occured in the following files:\n%s' % errors.strip())
            requestmod(errors.split())
        sys.argv[:] = [__file__]
        listfiles()
        select = getselect()
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
    try:
        select = console.raw_input('number > ')
        if select != '':
            select = int(select)
    except KeyboardInterrupt:
        exit('Goodbye!')
    if select == None:
        return getselect()
    return select

#die, error
def exit(msg):
    print(msg)
    sys.exit(1)


if "__main__" == __name__:
    sys.exit(build())


