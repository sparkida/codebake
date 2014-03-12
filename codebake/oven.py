"""
Codebake
Clean CSS, HTML, and JavaScript Files
v1.0
Author: Nicholas Riley
"""

#TODO - File concatenate
#TODO - Insert seperator --sep-text --sep-file?
#TODO* - switch lists for collections.deque and profile results
#TODO Optimize mixin block variables with bake

import sys
from os import path,name
from argparse import ArgumentParser

		
class Codebake(object):
	msg = {
			'noFile' 	: 'File not found!',
			'noEmpty' 	: 'File path cannot be empty!',
			'noArgs' 	: 'Expecting argument: file path!',
			'newline'	: '\n----------------------------\n'
			}
	subsituteVars = {
			'true'		: '!0',
			'false'		: '!1'
			#caused errors when undefined is parameter
			#'undefined'	: 'void 0'
			}
	#if -d opt overwrite config with defaultOpts
	defaultOpts = {
			#'saveHeader' 	: True,
			'subsitute'		: True,
			'obfuscate'		: True,
			'extras'		: True
			}
	#TODO - seperate javascript specific functions
	config = {
			'filepath'			: False,
			'format' 			: 'js',
			#'string'			: False,
			'force'				: False,
			'saveHeader'		: False,
			'extras'			: False,
			'obfuscate'			: False,
			'subsitute'			: False,
			'writepath'			: False,
			'verbose'			: False,
			'defaults'			: False,
			'chunk'				: 0
			}
	stats = {
			'originalSize'		: None,
			'originalPath'		: None,
			'compileSize'		: None,
			'outputPath'		: None
			}
	
	
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
		self.userVars = {}
		self.exchangeCount = 0
		self.skip = 0
		self.count = 0
		self.code = ''
		self.data = ''
		self.args = None
		self.chunkCount = 0
		self.stats = self.__class__.stats.copy()
		self.config = self.__class__.config.copy()

	def interact(self):
		"""create ArgumentParser object and call parseOpts"""	
		#parser info
		#build opts parser
		parser = self.parser = ArgumentParser(
				prog="Codebake", 
				description='Clean CSS, HTML, and JavaScript files.',
				epilog='',
				usage='codebake filepath\n\tcodebake [OPTIONS] [-f filepath]\n\tcodebake filepath [OPTIONS]')

		#parser.add_argument('-g', '--saveHeader', action='store_true', help='Saves only first comment of file. Implements -r.')
		parser.add_argument('-o', '--obfuscate', action='store_true', help='Use obfuscation.')
		parser.add_argument('-u', '--subsitute', action='store_true', help='Replace [true, false, undefined] with [!0, !1, void 0]')
		parser.add_argument('-e', '--extras', action='store_true', help='Remove extra commas and semicolons.')
		parser.add_argument('-v', '--verbose', action='store_true', help='Show stats at end.')
		parser.add_argument('-d', '--defaults', action='store_true', help='Sets the default attributes: -eou')
		parser.add_argument('-k', '--chunk', metavar='Number', type=int, help='Only strip newlines every (x) steps.(Useful when debugging)')
		parser.add_argument('-s', '--string', metavar='String', type=str, help='Read from string instead of file.')
		parser.add_argument('-t', '--format', metavar='Format', type=str, help='Set format for string: [js, css, html]. Default is "js".')
		parser.add_argument('-w', '--writepath', metavar='writepath', type=str, help='Write output to filepath.')
		#parser.add_argument('-x', '--force', action='store_true', help='Forces overwriting and saving of files as well as the creation of directories.')
		parser.add_argument('-f', '--filepath', metavar='filepath', type=str, help='Path of file to bake.')
		#check opts and run the parser
		self._parseOpts(0,1)


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
			if command[0] != '-':
				if path.isfile(path.realpath(command)):
					sys.argv.insert(1, '-f')
					argLength += 1
				else:
					self.noFile('noFile')
					return
		#end shell command hook
		#TODO - rewrite below to access an api module
		if argLength < 3:
			if argLength > 1:
				#check for help
				if sys.argv[1] == '-h' or sys.argv[1] == '--help':
					self.parser.print_help()
					if interactive and self.isatty:
						self.console.restart()
				#check for exit
				elif sys.argv[1] == 'exit':
					self.quit()
				return
			elif self.isatty:
				#force interactive mode
				self.interactive = 1
				if self.console == None:
					'''the console will add to the execution time, so only add it if needed'''
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
					print('-----Codebake-----')
					self.parser.print_help()
				elif not force:
					print('Error: Invalid Filepath : use -h for help')
					#start console
				self.console.restart()
			else:
				print('Error: required [-f Filepath]')
				sys.exit(1)

		#get args, #fail if no filepath provided
		filepathFailed = False

		#set arguments as settings
		#try:
		if self.interactive:
			try:
				self.args = vars(self.parser.parse_args(sys.argv[1:len(sys.argv)]))
			except:
				self.console.restart()
				return
		else:
			self.args = vars(self.parser.parse_args())
		for arg in self.args:
			if arg in self.config and self.args[arg]:	
				self.config[arg] = self.args[arg]
		
		if self.config['defaults']:
			for arg in self.defaultOpts:
				self.config[arg] = self.defaultOpts[arg]
		"""
		except:
			if not self.isatty:
				sys.stdout.write('0')
				sys.exit(1)
		"""
		#print(self.config)
		#turn into namespace
		#self.config = Bind(self.config)
		if 'string' not in self.config:
			#lastly verify that there is a file
			self.checkFileName()
		#get new fogged code
		"""just pass by reference, don't copy->i.e
		init = {
				'chunkCount': self.chunkCount,
				'exchangeCount': self.exchangeCount,
				'subsituteVars': self.subsituteVars,
				'userVars': self.userVars,
				'userStrings': self.userStrings,
				'config': self.config,
				'chunkCount': self.chunkCount,
				'skip': self.skip,
				'complete': self.complete,
				'get': self.get,
				'stats': self.stats
				}
		"""
		from bake import fetch
		fetch(self)

	def get(self, index):
		try:
			return self.data[index]
		except IndexError:
			return False
	
	#restart interactive console
	def restart(self):
		#reset args
		sys.argv = [sys.argv[0]]
		self.__reload()
		self.console.restart()
		return

	#handle final closing operations
	def complete(self):
		if self.isatty:
			if self.stats['outputPath'] == None:
				print(''.join(self.data))
			else:
				print('File created: %s' % self.stats['outputPath'])
			if self.config['verbose']:
				print(self._getStats())
			if self.interactive:
				self.restart()
				return
		self.quit(1)

	#get file name from input
	def noFile(self, msgType):
		if msgType != None:
			print(self.__class__.msg[msgType])
			if not self.isatty or self.isatty and not self.interactive:
				self.quit(1)
		self.restart()

	#make sure file exists
	def checkFileName(self):
		if not self.config['filepath']:
			self.noFile('noEmpty')
		elif not path.isfile(self.config['filepath']):
			self.noFile('noFile')

	def _getStats(self):
		string = ''
		end = '\n' if self.isatty else ';'
		sep = ': ' if self.isatty else '='

		for stat in self.stats:
			if self.stats[stat] != None:
				string += stat + sep + str(self.stats[stat]) + end
		return string.rstrip()

	#quit with message
	def quit(self, msg = ''):
		if msg != '':
			if msg == 1:
				sys.exit()
			else:
				if self.config['verbose']:
					print(_getStats())
				sys.exit(msg)
		else:
			sys.exit("Goodbye!\n")
