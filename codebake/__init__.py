#!/usr/bin/env python
"""
Codebake
Clean CSS, HTML, and JavaScript Files
v1.0
Author: Nicholas Riley
"""
#TODO - File concatenate
#TODO - Insert seperator --sep-text --sep-file?

#includes
import sys
from os import path,name
from argparse import ArgumentParser

		
class Bind(object):
	def __init__(self, dct):
		self.__dict__.update(dct)
	def get(self, index):
		try:
			return self.__dict__[index]
		except:
			return False
	
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
	commands = [
			'cd',
			'ls',
			'cat',
			'echo',
			'pwd',
			'touch',
			'vim',
			'gedit',
			'rm',
			'mkdir',
			'rmdir',
			'clear',
			'reset'
			]
	config = {
			'filepath'			: False,
			'string' 			: False,
			'format' 			: 'js',
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
			'compilePath'		: None
			}
	
	
	def __init__(self):
		#holds all variables going to
		self.parser = None
		self.console = None
		self.commands = self.__class__.commands
		self.isatty = sys.stdout.isatty()
		self.__reload()
		self.interact()

	def __reload(self):
		#reset user settings
		self.userStrings = dict()
		self.userVars = dict()
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
			
		#parser info
		#build opts parser
		parser = self.parser = ArgumentParser(
				prog="Codebake", 
				description='Clean CSS, HTML, and JavaScript files.',
				epilog='Interactive commands: ' + ', '.join(self.commands),
				usage='codebake filepath\n\tcodebake [OPTIONS] [-f filepath]\n\tcodebake filepath [OPTIONS]')

		#parser.add_argument('-g', '--saveHeader', action='store_true', help='Saves only first comment of file. Implements -r.')
		parser.add_argument('-o', '--obfuscate', action='store_true', help='Use obfuscation.')
		parser.add_argument('-u', '--subsitute', action='store_true', help='Replace [true, false, undefined] with [!0, !1, void 0]')
		parser.add_argument('-e', '--extras', action='store_true', help='Remove extra commas and semicolons.')
		parser.add_argument('-v', '--verbose', action='store_true', help='Show stats at end.')
		parser.add_argument('-d', '--defaults', action='store_true', help='Sets the default attributes: -eou')
		parser.add_argument('-k', '--chunk', metavar="\b=Number", type=int, help='Only strip newlines every (x) steps.(Useful when debugging)')
		parser.add_argument('-s', '--string', metavar='\b=String', type=str, help='Read from string instead of file.')
		parser.add_argument('-t', '--format', metavar='\b=Format', type=str, help='Set format for string: [js, css, html]. Default is "js".')
		parser.add_argument('-w', '--writepath', metavar='\b=writepath', type=str, help='Write output to filepath.')
		#parser.add_argument('-x', '--force', action='store_true', help='Forces overwriting and saving of files as well as the creation of directories.')
		parser.add_argument('-f', '--filepath', metavar='\b=filepath', type=str, help='Path of file to bake.')
		#check opts and run the parser
		self._parseOpts(0,1)


	def _parseOpts(self, interactive=0, fresh=0, force=0):
		self.interactive = interactive
		argLength = len(sys.argv)
		#hook for shell commands
		procFail = 1
		try:
			#check for command, execute and restart console
			if sys.argv[1] in self.commands:
				import subprocess
				procFail = subprocess.call(sys.argv[1:len(sys.argv)])
				#restart
				self.restart()
				return
			#check if file exists and restart with proper params
			elif sys.argv[1] != '' and sys.argv[1][0:1] != '-':
				if path.isfile(sys.argv[1]):
					sys.argv.insert(1, '-f')
					argLength += 1
				else:
					self.noFile('noFile')
					return

		except IndexError:
			#no params passed
			pass
		#end shell command hook
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
					from cli import Console
					self.console = Console()
					def restart(fresh = 0):
						#cli capture
						try:
							opts = self.console.raw_input('codebake > ')
						except KeyboardInterrupt:
							#bye
							print()
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
		'''
		except:
			if not self.isatty:
				sys.stdout.write('0')
				sys.exit(1)
		'''
		#print(self.config)
		#turn into namespace
		#self.config = Bind(self.config)
		if not self.config['string']:
			#lastly verify that there is a file
			self.checkFileName()
		#get new fogged code
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
			if self.stats['compilePath'] == None:
				print(''.join(self.data))
			else:
				print('File created: %s' % self.stats['compilePath'])
			if self.config['verbose']:
				print(self._getStats())
			if self.interactive:
				self.restart()
				return
		else:
			sys.stdout.write(''.join(self.data))
		self.quit('1')

	#get file name from input
	def noFile(self, msgType):
		if msgType != None:
			print(self.__class__.msg[msgType])
			if not self.isatty or self.isatty and not self.interactive:
				self.quit('1')
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
		if msg.__len__() > 0:
			if msg == '1':
				sys.exit()
			else:
				if self.config['verbose']:
					print(_getStats())
				sys.exit(msg)
		else:
			sys.exit("Goodbye!\n")

#get it going
if __name__ == '__main__':
	Codebake()


