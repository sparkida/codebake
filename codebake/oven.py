# -*- coding: utf-8 -*-
"""
Codebake
Clean CSS, HTML, and JavaScript Files
Author: Nicholas Riley
"""

#TODO - Insert seperator --sep-text --sep-file?
#TODO - switch lists for collections.deque and profile results
#TODO Optimize mixin block variables with bake

import sys
from os import path, sep, makedirs, unlink
from argparse import ArgumentParser

__version__ = '1.4.3' 
                
class Codebake(object):

    msg = {
            'noFile'    : 'File not found!',
            'noFormat'  : 'Could not determine format, please set --format.',
            'noEmpty'   : 'File path cannot be empty!',
            'noArgs'    : 'Expecting argument: file path!',
            'newline'   : '\n----------------------------\n'
            }
    subsituteVars = {
            'true'              : '!0',
            'false'             : '!1'
            #caused errors when undefined is parameter
            #'undefined'        : 'void 0'
            }
    #if -d opt overwrite config with defaultOpts
    defaultOpts = {
            'subsitute'         : True,
            'obfuscate'         : True,
            'saveHeader'        : True,
            'extras'            : True
            }
    #TODO - seperate javascript specific functions
    config = {
            'purge'                     : False,    
            'empty'                     : False,
            'filepath'                  : False,
            'format'                    : '',
            'recipe'                    : False,
            'stripx'                    : False,
            'copy'                      : False,
            'symlink'                   : False,
            #'string'                   : False,
            'force'                     : False,
            'saveHeader'                : False,
            'compileAll'                : False,
            'watch'                     : False,
            'extras'                    : False,
            'obfuscate'                 : False,
            'subsitute'                 : False,
            'writepath'                 : False,
            'verbose'                   : False,
            'defaults'                  : False,
            'generate'                  : False,
            'chunk'                     : 0
            }
    stats = {
            'originalSize'              : None,
            'originalPath'              : None,
            'compileSize'               : None,
            'writepath'                : None
            }

    globalConfigSet = False
    datetime = None
    createdDirs = set()
        

    def __init__(self):
        #holds all variables going to
        self.parser = None
        self.console = None
        self.isatty = sys.stdout.isatty()
        self.__reload()
        self.interact()

    def __reload(self):
        #reset user settings
        self.userStrings = {}
        self.userVars = set()
        self.userVarsFreq = None
        self.exchangeCount = 0
        self.skip = 0
        self.count = 0
        self.code = ''
        self.data = ''
        self.data = ''
        self.man = None
        self.manConfig = None
        self.args = None
        self.chunkCount = 0
        self.stats = self.__class__.stats.copy()
        self.config = self.__class__.config.copy()

    def setGlobalConfig(self, useIni = True):
        if self.globalConfigSet:
            return
        if useIni:
            if not path.exists('./bake.ini'):
                raise IOError('Codebake > no bake.ini found!')
            from ConfigParser import ConfigParser
            self.ini = ConfigParser()
            self.ini.read('./bake.ini')
            self.iniSrc = self.ini.get('compile', 'src')
            self.iniDestination = self.ini.get('compile', 'destination')
            self.relSrcPath = path.relpath(path.abspath(path.dirname(self.iniSrc)))
            self.relDestinationPath = path.relpath(path.abspath(path.dirname(self.iniDestination)))
        else:
            self.relSrcPath = path.relpath(path.abspath(path.dirname(self.config['filepath'])))
            if self.config['writepath']:
                self.relDestinationPath = path.relpath(path.abspath(path.dirname(self.config['writepath'])))
            else:
                self.relDestinationPath = self.relSrcPath
        self.globalConfigSet = True

    def update(self, watch, filepath, mask):
        basepath = path.basename(filepath.path)
        if basepath == '4913':
            #ignore vim update
            return
        print('\033[0;29mUpdating[%s]:\033[0;m \033[0;36m%s\033[0;m'  % (
                    self.datetime.today().strftime('%I:%M:%S'), 
                    basepath))
        self.prepFile(filepath.path)
        try:
            self.baker(self)
        except:
            print('Error Occured: 0x001')
        else:
            print('\033[0;32mFile Updated!\033[0;m')


    def watch(self):
        from bake import BakeJS
        from datetime import datetime
        from twisted.internet import reactor
        from twisted.internet import inotify
        from twisted.python import filepath
        self.baker = BakeJS
        self.datetime = datetime
        self.setGlobalConfig()
        notifier = inotify.INotify()
        notifier.startReading()
        notifier.watch(
                filepath.FilePath(self.relSrcPath),
                mask=4,
                autoAdd=True,
                callbacks=[self.update],
                recursive=True)
        #save for good measure
        #log = path.join(path.abspath(path.dirname(path.realpath(__file__))), 'bake.log')
        #fh = open(log, 'w')
        from os import devnull
        fh = open(devnull, 'w')
        stderr = sys.stderr
        sys.stderr = fh
        while True:
            try:
                reactor.run()
            except:
                fh.close()
                sys.stderr = stderr
                break
        self.quit('...\n\033[0;33m---killing watcher-->\033[0;m')

    def interact(self):
        """create ArgumentParser object and call parseOpts"""   
        #parser info
        #build opts parser
        parser = self.parser = ArgumentParser(
                prog="Codebake", 
                description='Clean CSS, HTML, and JavaScript files.',
                epilog='',
                usage='codebake filepath\n\tcodebake [OPTIONS] [-f filepath]\n\tcodebake filepath [OPTIONS]')
        add = parser.add_argument
        add('command', metavar='watch', nargs='?', default=False,
                        help='Watch the current directory for updates - [only .js].')
        add('command', metavar='all', nargs='?', default=False,
                        help='Recursively compiles all scripts in directory.')
        add('-o', '--obfuscate', action='store_true', 
                        help='Use obfuscation.')
        add('-c', '--copy', action='store_true',
                        help='Directly copy the file from filepath to writepath, no other actions are performed.')
        add('-l', '--symlink', action='store_true',
                        help='Create symlink(s) of the file from filepath to writepath, no other actions are performed.')
        add('-p', '--purge', action='store_true',
                        help='Purge created symlink(s), no other actions are performed.')
        add('-u', '--subsitute', action='store_true',
                        help='Replace [true, false, undefined] with [!0, !1, void 0]')
        add('-e', '--extras', action='store_true',
                        help='Remove extra commas and semicolons.')
        add('-v', '--verbose', action='store_true', 
                        help='Show stats at end.')
        add('-d', '--defaults', action='store_true', 
                        help='Sets the default optimal attributes; same as -oue')
        add('-g', '--generate', action='store_true',
                        help='Generate documents from code using SpkMan Syntax.')
        add('-i', '--save-header', action='store_true', 
                        help='Save first document comment; for licensing, about author, general info, etc...')
        add('-k', '--chunk', metavar='NUMBER', type=int, 
                        help='Only strip newlines every (x) steps.(Useful when debugging)')
        add('-s', '--string', metavar='STRING', type=str, 
                        help='Read input from string instead of file.')
        add('-t', '--format', metavar='EXT', type=str, 
                        help='Set format for string(-s): [js, css, html]. Default is "js".')
        add('-x', '--stripx', metavar='VALUES...', type=str,
                        help='Will remove all function calls to a list of objects: -x"dbg,console.log"'\
                                 'will remove all dbg() and console.log() calls')
        add('-w', '--writepath', metavar='FILEPATH', type=str,
                        help='Write output to filepath.')
        add('-f', '--filepath', metavar='FILEPATH', type=str, 
                        help='Path of file to bake.')
        add('-r', '--recipe', metavar='FILEPATH', type=str, 
                        help='A recipe of files to bake(concatenate)')
        #parser.add_argument('-', '--force', action='store_true', 
                        #help='Forces overwriting and saving of files as well as the creation of directories.')
        #check opts and run the parser
        self._parseOpts(0, 1)


    def _parseOpts(self, interactive=0, fresh=0, force=0):
        """parse arguments into options"""
        self.interactive = interactive
        argLength = len(sys.argv)
        #hook for shell commands
        procFail = 1
        command = None
        try:
            command = sys.argv[1]
        except IndexError:
            pass
        else:
            #make sure it isn't part of an ArgumentParser option
            if command[0] != '-' and command not in ['all','watch']:
                if path.isfile(path.realpath(command)):
                    sys.argv.insert(1, '-f')
                    argLength += 1
                else:
                    self.noFile('noFile')
                    return
        if command in ['-v', '--verbose']:
            print('Codebake v%s' % __version__)
        #end shell command hook
        if command in ['watch', 'all']:
            """set positional parameters"""
            if command == 'all':
                self.config['compileAll'] = True
            elif command == 'watch':
                self.config['watch'] = True
            sys.argv.pop(1)
        elif argLength < 3:
            """shorthand bake method, just pass files, default options assumed"""
            if argLength > 1:
                #check for help
                if command in ['-h', '--help']:
                    self.parser.print_help()
                    if self.interactive and self.isatty:
                        self.console.restart()
                    return
                #check for exit
                elif command == 'exit':
                    self.quit()
                    return
                self.noFile('noEmpty')
                raise StandardError('Codebake > Invalid format')
            elif self.isatty:
                #force interactive mode
                self.interactive = 1
                if self.console == None:
                    """the console will add to the execution time, so only add it if needed"""
                    from cli import Console
                    self.console = Console()
                    def restart(fresh = 0):
                        #cli capture
                        try:
                            opts = self.console.raw_input('codebake > ')
                        except KeyboardInterrupt:
                            #bye
                            self.quit()
                        #add __file__ to new args + opts
                        sys.argv = [sys.argv[0]] + opts.split()
                        self._parseOpts(1, fresh)
                    self.console.restart = restart
                #process fail, no user processes matched below
                if fresh:
                    #print startup message
                    print('-----Codebake v%s-----' % __version__)
                    self.parser.print_help()
                elif not force:
                    print('Error: Invalid Filepath : use -h for help')
                    #start console
                while True:
                    try:
                        self.console.restart()
                    except StandardError:
                        pass
                    except KeyboardInterrupt:
                        break
                self.quit()
            else:
                print('Error: required [-f Filepath]')
                sys.exit(1)
        #get args, #fail if no filepath provided
        filepathFailed = False
        #set arguments as settings
        #try:
        if self.interactive :
            try:
                self.args = vars(self.parser.parse_args(sys.argv[1:len(sys.argv)]))
            except:
                self.console.restart()
                return
        else:
            self.args = vars(self.parser.parse_args())
        #bind args to config prototype
        for arg in self.args:
            if arg in self.config and self.args[arg]:   
                self.config[arg] = self.args[arg]

        if self.config['generate']:
            from documentor import GenerateDoc
            #run the manual builder
            GenerateDoc(self)
            return

        if self.config['defaults']:
            for arg in self.defaultOpts:
                self.config[arg] = self.defaultOpts[arg]
        
        recipe = self.config['recipe']
        files = None
        
        if self.config['watch']:
            print('Codebake v%s: Watcher\n----------------------\n' % __version__)
            self.compileAll()
            self.watch()
            return
        elif self.config['compileAll']:
            self.compileAll()
            return
        elif recipe:
            with open(recipe, 'r') as fh:
                recipeType = fh.readline().strip()
                if recipeType[0] != '[':
                    raise StandardError('First line of recipe must specify a format, ie: [js] or [css]')
                recipeType = recipeType[1:-1]
                files = set([ x.strip() for x in fh.readlines() ])
            #build main file    
            composite = []
            glue = composite.append
            for f in files:
                filename = '%s.%s' % (f, recipeType)
                with open(filename, 'r') as fh:
                    #TODO - add in optional file markers
                    glue(''.join(fh.readlines()))
            self.config['string'] = ''.join(composite)
            self.config['format'] = recipeType
        elif 'string' not in self.config:
            #self.checkFileName()#moved below 
            if not self.config['filepath']:
                self.noFile('noEmpty')
            elif not path.isfile(self.config['filepath']):
                self.noFile('noFile')
            if self.config['format'] == '':
                try:
                    filename, ext = path.splitext(self.config['filepath'])
                except AttributeError:
                    """capture filepath=False"""
                    self.noFile('noEmpty')
                    return
                else:
                    if ext == '':
                        self.noFile('noFormat')
                    else:
                        self.config['format'] = ext[1:]

        #bake single file...
        self.setGlobalConfig(False)
        self.makedirs()
        ext = self.config['format']
        if 'js' == ext:
            from bake import BakeJS
            BakeJS(self)
        elif 'css' == ext:
            from bake import BakeCSS
            BakeCSS(self)
        elif 'html' == ext or 'htm' == ext:
            from bake import BakeHTML
            BakeHTML(self)
        else:
            raise StandardError('Codebake > Invalid format')

    def prepFile(self, filepath, synchronize = False):
        """resolve the filepath and update config"""
        basedir = path.abspath(self.relSrcPath)
        if basedir in filepath:
            filepath = '.%s' % filepath.split(basedir)[1]
        normpath = path.normpath(filepath)
        destination_filepath = path.join(self.relDestinationPath, normpath)
        if (self.config['symlink'] or self.config['purge']) \
                and path.islink(destination_filepath):
            if self.config['verbose']:
                print('removing old symlink: %s' % destination_filepath)
            unlink(destination_filepath)
        elif synchronize and path.exists(destination_filepath) and \
                path.getmtime(filepath) <= path.getmtime(destination_filepath):
            if self.config['verbose']:
                print('skipping: %s ' % filepath)
            return False
        self.config['writepath'] = destination_filepath
        self.config['filepath'] = filepath
        self.makedirs(path.dirname(destination_filepath))
        return True
    
    def makedirs(self, dirname = ''):
        if dirname == '':
            try:
                self.config['writepath'] = path.join(self.relDestinationPath, self.config['writepath'])
            except AttributeError:
                pass
            return
        if dirname not in self.createdDirs:
            self.createdDirs.add(dirname)
            if not path.isdir(dirname):
                if self.config['verbose']:
                    print('Making directories: %s' % dirname)
                makedirs(dirname)

    def compileAll(self):
        """compile all javascript files found in self.relSrcPath"""
        self.setGlobalConfig()
        from subprocess import Popen, PIPE
        from bake import BakeJS
        #find all javascript files
        paths = Popen('find %s -name "*.js"' % self.relSrcPath, stdout=PIPE, shell=True)
        stdout, stdin = paths.communicate()
        stdout = stdout.strip().split('\n')
        verbose = self.config['verbose']
        copy = self.config['copy']
        symlink = self.config['symlink']
        if copy:
            from shutil import copyfile
        elif symlink:
            from os import symlink
            fileExists = path.exists
        for filepath in stdout:
            if not self.prepFile(filepath, False if symlink or copy else False):
                continue
            if copy:
                copyfile(self.config['filepath'], self.config['writepath'])
            elif symlink:
                sympath = path.abspath(self.config['writepath'])
                srcpath = path.abspath(self.config['filepath'])
                if fileExists(sympath):
                    unlink(sympath)
                if verbose:
                    print('Linking: %s -> %s' % (sympath, srcpath))
                symlink(srcpath, sympath)
            else:
                BakeJS(self)
        self.config['watch'] or self.quit(1)

    def get(self, index):
        try:
            return self.data[index]
        except IndexError:
            return False
    
    def restart(self):
        """restart interactive console"""
        sys.argv = [sys.argv[0]]
        self.__reload()
        self.console.restart()
        return

    def complete(self):
        """handle final closing operations"""
        compileAll = self.config['compileAll']
        watch = self.config['watch']
        if self.config['writepath']:
            writepath = self.config['writepath']
            if self.config['verbose']:
                print('writing: %s' % writepath)
            with open(writepath, 'w') as fp:
                fp.write(self.data)
        else:
            print(self.data)
        if self.isatty:
            if self.config['verbose']:
                #TODO - make into json for api front
                print(self._getStats())
            if self.interactive and not compileAll and not watch:
                self.restart()
                return
        if not compileAll and not watch:
            self.quit(1)

    def noFile(self, msgType):
        """get file name from input"""
        if msgType != None:
            print(self.__class__.msg[msgType])
            if not self.isatty or self.isatty and not self.interactive:
                self.quit(1)
        self.restart()

    def _getStats(self):
        """get info for compiled file"""
        string = ''
        end = '\n' if self.isatty else ';'
        sep = ': ' if self.isatty else '='

        for stat in self.stats:
            if self.stats[stat] != None:
                string += stat + sep + str(self.stats[stat]) + end
        return string.rstrip()

    def quit(self, msg = ''):
        """quit with message"""
        if msg != '':
            if msg == 1:
                sys.exit()
            else:
                if self.config['verbose']:
                    print(self._getStats())
                sys.exit(msg)
        else:
            sys.exit("Goodbye!\n")


class RecurseBake(object):
    
    """
    Dummy Codebake, for recursive bakes...
    typically when baking HTML with inline CSS/JS
    """
    
    def __init__(self, data):
        """holds all variables going to..."""
        self.parser = None
        self.console = None
        self.__reload()
        self.config['string'] = data

    def __reload(self):
        """reset user settings"""
        self.userStrings = {}
        self.userVars = {}
        self.exchangeCount = 0
        self.skip = 0
        self.count = 0
        self.code = ''
        self.data = ''
        self.args = None
        self.chunkCount = 0
        self.stats = Codebake.stats.copy()
        self.config = Codebake.config.copy()

    def get(self, index):
        try:
            return self.data[index]
        except IndexError:
            return False
    
    def complete(self):
        self.data = ''.join(self.data)


if __name__ == '__main__':
    Codebake()


