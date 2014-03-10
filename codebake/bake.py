"""
Codebake
Clean CSS, HTML, and JavaScript Files
v1.0
Author: Nicholas Riley
"""

import re
from os import path, sep, makedirs

'''
Generator
Provides key creation and obfuscation values
'''
class Generator(object):
	#constants
	maxRange = 26
	upperCase = 65
	upperCaseMax = upperCase + maxRange
	lowerCase = 97
	lowerCaseMax = lowerCase + maxRange
	count = 0
	laps = 0
	rounds = 0
	useLower = True
	useUpper = False
	block = ['in','do','if']

	def __init__(self):
		self.used = []
		self.block = set(self.__class__.block)

	def alpha(self):
		if self.laps == 0:
			#first lap, single digit lower
			char = chr(self.lowerCase + self.count)
		elif self.laps == 1:
			#single digit upper
			char = chr(self.upperCase + self.count)
		elif self.laps <= 25 and self.useLower:
			#double digit lower
			charA = chr(self.lowerCase + self.laps-2) 
			char = charA + chr(self.lowerCase + self.count)
			if char in self.block:
				self.count += 1
				char = charA + chr(self.lowerCase + self.count)
		else:
			if self.useUpper:
				charB = chr(self.upperCase + self.count)
			else:
				charB = chr(self.lowerCase + self.count)
			char = chr(self.upperCase + self.laps) + charB

		#increase count
		self.count += 1
		#check for lap update and reset
		if self.count >= self.maxRange:
			self.count = 0
			self.laps += 1
			if self.laps == 26:
				self.laps = 0
				self.rounds += 1
				self.useLower = False
				if self.rounds == 26:
					self.useUpper = true
		
		self.used.append(char)
		#return character
		return char
			

def fetch(Main):
	if Main.config['subsitute']:
		Main.userVars = Main.subsituteVars.copy()
	gen = Generator()
	genAlpha = gen.alpha
	filepath = Main.config['filepath']
	regexList = {
		'removeDbg'				: r'(dbg\(.*\)[,\|;]?)',
		'removeLineComments' 	: r'([\h\t]*/{2}.*[\r\n]?)',
		'removeDocComments'		: r'(/\*.*?(?<=\*/))',
		'replaceString'			: r'((?<!/)/[^*/\n\s].*?[^\\]/[igm]{0,3})|((?P<qt>[\'"]).*?(?<!\\)(?P=qt))|(([0-9]x[a-zA-Z0-9]+)|(([0-9]+\.?)+))'
	}

	#build regex commands
	regex = regexList['removeDbg'] + '|' + regexList['removeLineComments']
	regexMulti = re.compile(r'%s' % regexList['removeDocComments'], re.MULTILINE | re.DOTALL)
	
	#create and return reference to string
	def stringExchange(string):
		#create an exchange reference
		exchangeRef = '@S_%d' % Main.exchangeCount
		Main.exchangeCount += 1
		#add to user stored strings
		Main.userStrings[exchangeRef] = string.group(0)
		return exchangeRef
	
	#capture function parameters and define as vars
	def functionCapture(string):
		match = re.sub(r'[^\w]',' \r',string.group(1)).split()
		if len(match):
			for name in match:
				if name not in Main.userVars:					
					Main.userVars[name] = genAlpha()
		return string.group(0)
	
	def chunk(string):
		if Main.config['chunk'] == Main.chunkCount:
			Main.chunkCount = 1
			return ' @_n '
		Main.chunkCount += 1


	#read file if not string
	if 'string' not in Main.config:
		#get file from arg
		with open(filepath) as fp:
			#removeDocComments
			Main.data = re.sub(regexList['replaceString'], stringExchange, fp.read())
	else:
		Main.data = re.sub(regexList['replaceString'], stringExchange, Main.config['string'])
		#removeDocComments
	
	#remove line comments and dbg statements
	Main.data = regexMulti.sub('', Main.data)
	Main.data = re.sub(regex, '', Main.data)
	#Main.data = re.sub(regexList['replaceRegex'], stringExchange, Main.data)

	if Main.config['obfuscate']:
		#capture function params
		#TODO
		#TODO
		#TODO
		#TODO - capture through  iterative process with an id so we can identify and
		#instantiate unique generators per function or similar workaround
		Main.data = re.sub(r'function\((.*?\))', functionCapture, Main.data)
	#if not Main.config['whitespace']:
	#Main.data = re.sub(' ', ' @_s ', Main.data)
	#Main.data = re.sub('\t', ' @_t ', Main.data)

	if Main.config['chunk']:
		Main.data = re.sub('\n', chunk, Main.data)
	#mark characters
	#seperate by anything that isn't valid character
	Main.data = re.sub(r'([^\w\d_@$])', r' \1 ', Main.data).split()
	#read string data
	spaceRequired = [
		'void',
		'new',
		'var',
		'typeof',
		'throw',
		'return',
		'delete'
	]
	dualSpaceRequired = [
		'instanceof',
		'in'
	]
	blockList = ['window','this','self','undefined','null']
	logic = [
			'=',
			'<',
			'>',
			'!'
			]
	assignment = [
			'=',
			'+',
			'/',
			'-',
			'*',
			'%'
			]

	config = Main.config
	blocked = set(spaceRequired + dualSpaceRequired + Generator.block + blockList)
	defaults = {} if not config['subsitute'] else Main.subsituteVars.copy()
	__set = set()
	__setAdd = __set.add
	operators = set([x for x in logic + assignment if x not in __set and not __setAdd(x)])
	assignment = set(assignment)
	logic = set(logic)
	spaceRequired = set(spaceRequired)
	dualSpaceRequired = set(dualSpaceRequired)
	skipChars = set([
			'"',
			"'",
			'.',
			',',
			'[',
			']',
			'{',
			'}',
			'|',
			'&',
			'?',
			'(',
			')',
			':',
			'/',
			r'\\'
			])
	blockList = set(blockList)
	'''
	def findTerminator(match, captureSymbol, index):
		capture = False
		func_levels = 0
		while True:
			test = Main.get(index)
			if test:
				if test == match:
					if func_levels == 0:
						return index
					else:
						func_levels -= 1
				elif test == captureSymbol:
					if not capture:
						capture = True
					else:
						func_levels += 1
			else:
				return False
			#increment by one
			index += 1
	'''
	skipBlock = set([
			' ',
			'\r',
			'\n',
			#'\t',
			'@_n'
			#'@_s',
			#'@_t'
			])




	#create classes to dunamically handle seeked indexes
	class Seeker(object):
		def __init__(self, instance = ''):
			self.index = 0
			self.lastIndex = None
			self.value = False
			self.instance = instance
			#self.count = 0

			#set the typeof Seeker object: prev | next

		def __call__(self, index = int, skip = 0):
			if self.lastIndex is not None and index == self.lastIndex:
				#self.count += 1
				return
			else:
				self.lastIndex = index
			self.index = index
			self.value = False
			#switch to try for ### reason
			if self.instance == 'prev':
				while self.index - 1 > 0:
					self.index -= 1
					# for heere ### we just want to do Main.data[self.index] and error
					self.value = mget(self.index)
					if self.value in skipBlock:
						continue
					elif skip > 0:
						skip -= 1
						continue
					else:
						break
			else:
				while True:
					self.index += 1
					# for heere ### we just want to do Main.data[self.index] and error
					self.value = mget(self.index)
					if not self.value:
						break
					if self.value in skipBlock:
						continue
					elif skip > 0:
						skip -= 1
						continue
					else:
						break

	seek = dict({'next':Seeker('next'),'prev':Seeker('prev')})
	count = 0
	genAlpha = gen.alpha
	mdata = Main.data
	mget = Main.get
	mskip = Main.skip
	insert = mdata.insert
	userStrings = Main.userStrings
	userVars = Main.userVars
	obfuscate = Main.config['obfuscate']
	seekprev = seek['prev']
	seeknext = seek['next']

	def obfuscateAdd(index):
		"""add main data value from index, to obfuscate list"""
		if obfuscate:
			value = mdata[index]
			v1 = value[0:1]
			if v1 != '/' and v1 != "'" and v1 != '"' and value not in blocked:
				seekprev(index)
				prev = seekprev.value
				#make sure it isn't part of an object
				#if it is a ternary then obfuscate
				if prev and prev != '.':
					seeknext(index)
					next1 = seeknext.value
					if not next1 or next1 != ':' or prev == '?':
						if value not in userVars:
							userVars[value] = genAlpha()
						#Main.data[index] = Main.userVars[value]

	for syntax in mdata:
		if mskip > 0:
			#print('skip--------------------------'+syntax)
			#print(mdata[count-2:count+2])
			#print(#skipmsg)
			mskip -= 1
			count += 1
			continue
		if syntax[0] == '@':
			_syntax3 = syntax[0:3]
			if _syntax3 == '@S_':
				mdata[count] = userStrings[syntax]
			elif config['chunk']:
				if _syntax3 == '@_n':
					mdata[count] = '\n'
				elif _syntax3 == '@_t':
					mdata[count] = '\t'
				elif _syntax3 == '@_s':
					mdata[count] = ' '
			count += 1
			continue
		elif syntax == '=':
			if obfuscate:
			#== , != , /= , += ,-=
			#grab defined name
			#if count == 0:
			#	Main.quit('File cannot begin with =')
			#el
				dist = 0
				skip = defName = False
				while count - (dist + 1) > 0:
					dist += 1
					defName = mdata[count - dist]
					if defName[0:3] == '@S_':
						skip = True
						break
						
					if defName != ' ' and defName != '\n' and defName not in operators and defName not in skipChars:
						break
				if skip or not defName:
					continue
				obfuscateAdd(count - dist)
		elif syntax != '=' and syntax != ';' and (syntax[0:1] in operators or syntax[0:1] in skipChars):
			#TODO - add characters to skip
			count += 1
			continue
		elif config['subsitute'] and syntax in defaults:
			mdata[count] = userVars[syntax]
		elif syntax in dualSpaceRequired:
			#if mdata[count-1] != ' ':
			#	insert(count, ' ')
			#	mskip += 1
			#TODO - continue this logic ^

			insert(count, ' ')
			insert(count + 2, ' ')
			mskip += 2
			#skipmsg = 'dualspace12'
		elif syntax == 'if':
			#next1 = mget(count + 1)
			seekprev(count)
			prev1 = seekprev.value
			if prev1 and prev1 == 'else':
				insert(count, ' ')
				mskip += 1
				#skipmsg = 'if12'
		else:
			#seeknext(count)
			seeknext(count)
			#next1 = seeknext.value or seeknext.value
			next1 = seeknext.value

			if not next1:
				break
			if syntax in spaceRequired:
				insert(count + 1, ' ')
				#skipmsg = 'spaceRequired55'
				#and skip all
				mskip += 1
			elif config['extras'] and syntax == ';':
				#opt -- remove extra semicolons
				if next1 == '}':
					#mskip += 1
					mdata[count:seeknext.index + 1] = ['}']
			elif syntax == 'case':
				#if not string
				if next1[0:3] != '@S_':
					insert(count + 1, ' ')
					mskip += 1
					#skipmsg = '@S_ 88'
			elif syntax == 'function':
				#TODO -- URGER
				#TODO -- URGER
				#TODO -- URGER --- MAKE SUB GENERATOR right before obfuscation
				#to re generate non-blocked list of stored uservar references

				#print('==========')
				#print(mdata[count-5:count+5])
				#print(mdata[seeknext.index])

				#grab defined function name
				#is function call started: "function("
				#if not add a space: "function foo(
				if next1 and next1 != '(':
					#set name
					obfuscateAdd(seeknext.index)
					insert(count + 1, ' ')
					mskip += 1
					#skipmsg = '(   909'
		count += 1

	if config['obfuscate']:
		count = 0
		#end for
		#Main.complete()
		skipChars.update([';','\n'] + list(operators))
		blocked = list(blocked)
		blocked += [x for x in ['case','new', 'void 0', 'if', 'else'] if x not in blocked]
		blocked2 = set(list(blockList) + list(dualSpaceRequired) + list(spaceRequired) + defaults.values())

		#print(gen.used)
		for syntax in mdata:
			#prev = mget(count - 1)
			if syntax[0:1] not in skipChars and syntax not in blocked and syntax not in blocked2:
				if syntax in userVars:
					dist = 0
					while True:
						dist += 1
						prev = mdata[count - dist]
						if not prev or (prev != ' ' and prev!= '\n'):
							break
					#make sure it isn't part of an object
					#if it is a ternary then obfuscate
					if prev and prev != '.':
						dist = 0
						while True:
							dist += 1
							next1 = mget(count + dist)
							if not next1 or (next1 != ' ' and next1 != '\n'):
								break
						if not next1 or next1 != ':' or prev == '?':
							mdata[count] = userVars[syntax]
			#increase by one
			count += 1
	print(mdata == Main.data)
	#final string!!!
	mdata = ''.join(mdata)

	

	#write to file
	if config['writepath']:
		expandPath = path.abspath(config['writepath'])
		dirPath = path.dirname(expandPath)

		if not path.isdir(dirPath):
			if Main.isatty:
				createDirs = checkDirs(dirPath)
				if not config['force']:
					answer = Main.console.raw_input('Create Directories[Yes/No]? > ').lower()
					if answer == 'yes' or answer == 'y':
						makedirs(createDirs)
				else:
					makedirs(createDirs)
			#not interactive
			elif not config['force']:
				Main.quit('Directories don\'t exists: use command option -x to force creation')
		with open(expandPath, 'w') as fp:
			fp.write(mdata)
		#update Main
		if config['verbose']:
			Main.stats.update({
				'originalPath'	: config['writepath'], 
				'compilePath'	: expandPath,
				'compileSize'	: path.getsize(expandPath)
				})
	elif config['verbose']:
		#update Main
		Main.stats['compileSize'] = mdata.__len__()

	if config['verbose']:
		if 'string' not in config:
			origSize = int(path.getsize(config['filepath']))
		else:
			origSize = config['string'].__len__()
		Main.stats['originalSize'] = origSize
		Main.stats['percent'] = int(round(100 / (float(Main.stats['originalSize']) / float((Main.stats['originalSize'] - Main.stats['compileSize'])))))
	#complete the clean
	Main.complete()


#check and display directories
def checkDirs(dirPath):
	dirs = dirPath.split(sep)[1:]
	count = 0
	isDir = True
	path = sep + dirs[0]
	while path.isdir(path):
		count += 1
		path += sep + dirs[count]
	path = sep+sep.join(dirs[0:count])
	dirs = dirs[count:len(dirs)]
	count = 0
	print("------------------\nDirectories don't exist:")
	for d in dirs:
		path += sep + d
		print(path)
	return path

	
