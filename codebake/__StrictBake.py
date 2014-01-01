"""
Codefog
Clean CSS, HTML, and JavaScript Files
v1.0
Author: Nicholas Riley
"""

import re
import random
import os
import sys

'''
Generator
Provides key creation and obfuscation values
'''
class Generator:
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

	def alpha(self):
		#first lap, single digit lower
		if self.laps == 0:
			char = chr(self.lowerCase + self.count)
		#single digit upper
		elif self.laps == 1:
			char = chr(self.upperCase + self.count)
		#double digit lower
		elif self.laps <= 25 and self.useLower:
			charA = chr(self.lowerCase + self.laps) 
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
					self.useUpper = True
		#return character
		return char
			

def fetch(Main):
	if Main.config.get('subsitute'):
		Main.userVars = Main.subsituteVars.copy()
	gen = Generator()
	filepath = Main.config.filepath
	regexList = {
		'removeDbg'				: r'(dbg\((.*)\)[,\|;]?)',
		'removeLineComments' 	: r'(/{2}(.*?[\r\n]))',
		'removeDocComments'		: r'(/\*(.*?\*/))',
		'replaceString'			: r'([\'].*?[\'])|(["].*?["])',
		'replaceRegex'			: r'=(\s+)?(/.*(?<!\\)/(.[igm]{0,3})?)'
	}
	#TODO - make these into opts --- set to all - temporary
	regex = regexList['removeDbg'] 
	if Main.config.lineComments:
		regex += '|' + regexList['removeLineComments']
	if Main.config.docComments:
		multiReg = re.compile(r'%s' % regexList['removeDocComments'], re.MULTILINE | re.DOTALL)
	

	def stringExchange(string):
		#create an exchange reference
		exchangeRef = '@S_' + str(Main.exchangeCount)
		Main.exchangeCount += 1
		#add to user stored strings
		Main.userStrings[exchangeRef] = string.group(0)
		return exchangeRef
	
	'''
	def displaymatch(match):
		if match is None:
			return None
		print('<Match: %r, groups=%r>' % (match.group(), match.groups()))
	'''

	def regexExchange(string):
		#displaymatch(string)
		#create an exchange reference
		exchangeRef = '@S_' + str(Main.exchangeCount)
		Main.exchangeCount += 1
		#add to user stored strings
		Main.userStrings[exchangeRef] = string.group(2)
		return '='+exchangeRef

	#capture function parameters and define as vars
	def functionCapture(string):
		match = re.sub(r'[^\w]',' \r',string.group(1)).split()
		if len(match):
			for name in match:
				if Main.userVars.get(name) == None:
					Main.userVars[name] = gen.alpha()
		return string.group(0)

	#read file if not string
	if not Main.config.string:
		#get file from arg
		with open(filepath) as f:
			Main.data = re.sub(regexList['replaceString'], stringExchange, f.read())
			#TODO - capture string from search replace etc first
			#strip dbg and line comments
	else:
		Main.data = re.sub(regexList['replaceString'], stringExchange, Main.config.string) 

	if Main.config.docComments:
		#removeDocComments
		Main.data = multiReg.sub('', Main.data)
	#replace strings and regex values -- must do
	Main.data = re.sub(regex, '', Main.data)
	#replace strings and regex values -- must do
	Main.data = re.sub(regexList['replaceRegex'], regexExchange, Main.data)
	if Main.config.obfuscate:
		#capture function params
		Main.data = re.sub(r'function\((.*?\))', functionCapture, Main.data)
	#seperate by anything that isn't valid character
	#if not Main.config.newlines:
	Main.data = re.sub('\n', ' @_n ', Main.data)
	#mark characters
	if not Main.config.whitespace:
		Main.data = re.sub('\t', ' @_t ', Main.data)
		Main.data = re.sub('\s', ' @_s ', Main.data)
	#seperate by anything that isn't valid character
	Main.data = re.sub(r'([^\w\d_@$])', r' \1 ', Main.data).split()
	#read string data
	parse(Main, gen)


#check if number or return false
def num(string):
	try:
		return int(string)
	except ValueError:
		pass
	try:
		return float(string)
	except ValueError:
		return False

#main js parser
def parse(Main, gen):
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
	blockList = [
			'null'
			#'false',
			#'true'
			]

	blocked = set(spaceRequired + dualSpaceRequired + gen.block + blockList)
	count = 0

	seekBlock = [
			' ',
			'\r',
			'\n',
			'\t',
			'@_n',
			'@_t',
			'@_s'
			]
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
	__set = set()
	__setAdd = __set.add
	operators = [x for x in logic + assignment if x not in __set and not __setAdd(x)]
	def getPrev(index):
		while True:
			index -= 1
			prev = Main.get(index)
			if not prev:
				return False
			elif prev in seekBlock:
				continue
			else:
				return {'index':index,'value':prev}
			
	def getNext(index, seek = 0):
		while True:
			index += 1
			next1 = Main.get(index)
			if not next1:
				return False
			elif next1 in seekBlock:
				continue
			elif seek > 0:
				seek -= 1
				continue
			else:
				return {'index':index,'value':next1}

	def findTerminator(match, captureSymbol=False, index=0):
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
				elif captureSymbol and test == captureSymbol:
					#start capturing
					if not capture:
						capture = True
					#hit symbol -> increase levels
					else:
						func_levels += 1
			else:
				return False
			#increment by one
			index += 1
	def getEnd(index):
		while True:
			index += 1
			seek = Main.get(index)
			if seek and seek != '@_n' and seek != ';' and seek != ',':
				continue
			else:
				if not seek:
					return False
				elif seek == '@_n':
					#check next for assignment operators
					prevSeek = getPrev(index)
					if prevSeek['value'] in assignment:
						return getEnd(index)
					else:
						nextSeek = getNext(index)
						if nextSeek and nextSeek['value'] in assignment:
							return getEnd(nextSeek['index'])
						else:
							return index
				break
	"""
	def closeFunction(index):
		#print(Main.data[index:index+6])
		next1 = getNext(index)
		if next1['value'] == ')':
			next2 = getNext(next1['index'])
			#(function(){})()
			if next2['value'] == '(':
				#get end starting from current + 1
				end = findTerminator(')', '(', next2['index'] + 1)
				next3 = getNext(end)
				if next3 and isOpen(next3['value']):
					Main.data.insert(end + 1, ';')
					Main.skip += 1
			'''
			#(function(){})
			elif next2 and isOpen(next2['value']):
				Main.data.insert(next1['index'] + 1, ';')
			'''
	"""

	def isOpen(value):
		return False if value == ',' or value == ';' or value == '}' else True

	newlineCount = 0

	#this will attempt to fix missing syntax
	for syntax in Main.data:
		if Main.skip > 0:
			Main.skip -= 1
			count += 1
			continue
		#Character Replace: invisible chars
		if syntax[0] == '@':
			char = syntax[1:3]
			if char == '_t':
				Main.data[count] = '\t'
			elif char == '_s':
				Main.data[count] = ' '
			elif char == '_n':
				if Main.config.newlines:
					if Main.config.steps > 0:
						if newlineCount == Main.config.steps:
							newlineCount = 0
							Main.data[count] = '\n'
						else:
							Main.data[count] = ''
							newlineCount += 1
				else:
					Main.data[count] = '\n'
		'''
		if syntax == 'if' or syntax == 'else' or syntax == 'return':
			prev = getPrev(count)
			if not prev:
				break
			prevV = prev['value']
			if prev and prevV != ';' and prevV != '}' and prevV != 'else' and prevV != '{':
				Main.data.insert(prev['index'] + 1, ';')
				
		#Syntax Fixer: definition started
		el
		'''
		if syntax == '=':
			nextObj = getNext(count)
			if not nextObj:
				#print('breaking 2')
				break
			next1 = nextObj['value']
			#check prev
			if next1 == 'function':
				#search for ending } and place a , or ;
				#get the index of closing bracket
				#function(){}
				match = findTerminator('}', '{', nextObj['index'] + 1)
				next2 = getNext(match)
				if not next2:
					#function end
					pass
				elif next2['value'] == '(':
					#function(){}()
					end = findTerminator(')', '(', next2['index'] + 1)
					next3 = getNext(end)
					if next3 and isOpen(next3['value']):
						Main.data.insert(end + 1, ';')
				#if function(){} !=},;
				elif isOpen(next2['value']):
					if next2['value'] != '}':
						Main.data.insert(match + 1, ';')
					#(function(){})()
					elif next2['value'] == 'function':
						Main.data.insert(match + 1, ';')
					elif next2['value'] == 'var':
						#resetting local var
						Main.data[match:match + 1] = ['}',';']
					else:
						#assume local var
						Main.data.insert(match + 1, ';')
			#elif next1[0:6] == '@Str__':
		#		#TODO
				#TODO
				#TODO
				#TODO
		#		next2 = getNext(nextObj['index'])
				#check for terminator
		#		if next2 and isOpen(next2['value']) and next2['value'] != '}':
		#			Main.data.insert(count + 2, ';')
		#	#foo=(
			elif next1 == '(':
				#end = findTerminator(')', '(', count + 1)
				next2 = getNext(nextObj['index'])
				#(function
				if next2 and next2['value'] == 'function':
					#(?function(){
					end = findTerminator('}', '{', next2['index'] + 1)
					next3 = getNext(end)
					#(?function(){})[,;]  --- is it closed?
					if next3 and isOpen(next3['value']):
						#(?function(){}(?
						if next3['value'] == '(':
							#(?function(){}()
							end2 = findTerminator(')', '(', next3['index'])
							#(?function(){}().
							next4 = getNext(end2)
							#(?function(){}()[^,;]
							if next4 and isOpen(next4['value']):
								if next4['value'] == ')':
									next4Count = next4['index'] - 1
									#make sure this is the last )
									while True:
										next4Count+=1
										index = getNext(next4Count)
										if index and index != ')':
											continue
										else:
											index = next4['index']
											break
									#get next and make sure it's open
									next5 = getNext(index)
									#(?function(){}())[^,;]
									if next5 and isOpen(next5['value']):
										Main.data.insert(index + 1, ';')
						#end -- (?function(){}(?
						#(?function(){})?
						elif next3['value'] == ')':
							next3Count = next3['index'] - 1
							#make sure this is the last )
							while True:
								next3Count+=1
								index = getNext(next3Count)
								if index and index != ')':
									continue
								else:
									index = next3['index']
									break

							next4 = getNext(index)
							#(?function(){})+?[^,;]
							if next4 and isOpen(next4['value']):
								#(?function(){})+?[^,;](?
								'''
								if next4['value'] == '(':
									end = findTerminator(')', '(', next4['index'])
									next5 = getNext(end)
									if next5 and isOpen(next5['value']):
										Main.data.insert(end + 1, ';')
								'''
								if next4['value'] != '(':

									Main.data.insert(index + 1, ';')
				#foo=(!function
				elif next2:
					#(.*)?
					end = findTerminator(')', '(', nextObj['index'])
					#(.*).
					next2 = getNext(end)
					#(.*)[^,;]
					if next2 and isOpen(next2['value']):
						Main.data.insert(end + 1, ';')


			elif next1 == 'typeof':
				end = getEnd(nextObj['index'])
				if end:
					prev = getPrev(end)
					if prev and isOpen(prev['value']):
						Main.data.insert(prev['index'] + 1, ';')



			#foo =[!=]?
			elif next1 not in operators:
				#foo [!=]?=
				prev = getPrev(count)
				if next1 == 'new' or (prev and prev['value'] not in operators):
					if next1 == 'new':
						nextObj = getNext(nextObj['index'])
					#check next foo = ?
					next2 = getNext(nextObj['index'])
					if next2 and isOpen(next2['value']):
						#={ } or  = []
						if next2['value'] == '{' or next2['value'] == '(':
							switch = '}' if next2['value'] == '{' else ')'
							end = findTerminator(switch, next2['value'], next2['index'])
							next3 = getNext(end)
							if next3 and isOpen(next3):
								Main.data.insert(end + 1, ';')							
						elif next2['value'] in assignment:
							nextCount = next2['index']
							#try to find line termination
							next3 = getEnd(nextCount)
							#newline terminated
							if next3:
								prev2 = getPrev(next3)
								if isOpen(prev2['value']):
									Main.data.insert(prev2['index'] + 1, ';')
						elif next2['value'] == '?':
							#get second part
							end = findTerminator(':', False, next2['index'] + 1)
							next3 = getNext(end)
							if next3:
								temp = getEnd(next3['index'])
								if temp:
									next4 = getPrev(temp)
									if next4 and isOpen(next4['value']):
										Main.data.insert(next4['index'] + 1, ';')
						elif (next2['value'] != '.' and next2['value'] != '0'
								and next2['value'] != ':' and next2['value'] != '['
								and next2['value'] != '{') and next2['value'] not in assignment:
							Main.data.insert(nextObj['index'] + 1, ';')

		#end syntax == '='?
		else:
			next1 = getNext(count)
			#check prev
			if next1 and next1['value'] == 'function':
				#search for ending } and place a , or ;
				#get the index of closing bracket
				match = findTerminator('}', '{', next1['index'] + 1)
				#get next character check for comma or semicolon
				next2 = getNext(match)
				if next2 and next2['value'] == ')':
					next3 = getNext(next2['index'])
					#(function(){})()
					if next3 and next3['value'] == '(':
						#get end starting from current + 1
						end = findTerminator(')', '(', next3['index'] + 1)
						next4 = getNext(end)
						if next4 and isOpen(next4['value']):
							Main.data.insert(end + 1, ';1')
							Main.skip += 1
			'''
			elif next1:
				next2 = getNext(next1['index'])
				if next2 and next2['value'] == '?':
					pass
			'''
			#capture var set = 'set' \n set2='set2' -> var set='set';set2='set2'
				#make this continues with a ';'
				#elif next2 != 'if' and next2 != 'else':
				#	if next2 == '(':
				#		next3 = findTerminator(')', '

			#elif next1 == 'var':
				#remove extras? remove [';', 'var'] and add ','
		count += 1


	count = 0
	skip = 0
	skipSpace = False
	for syntax in Main.data:
		if Main.skip > 0:
			#print('skip used')
			Main.skip -= 1
			count += 1
			continue
		if type(num(syntax)) == int:
			count += 1
			blocked.update([syntax])
			continue
		elif syntax in dualSpaceRequired:
			#TODO
			#TODO
			#TODO
			#TODO
			prev = Main.data[count - 1]
			next1 = Main.data[count + 1]
			if prev and prev != ' ':
				Main.data.insert(count, ' ')
			elif next1 and next1 != ' ':
				Main.data.insert(count + 1, ' ')
		elif syntax in spaceRequired:
			if syntax == 'return':
				nextObj = getNext(count)
				next1 = nextObj['value']
				if not next1:
					pass
				#opt -- remove extra semicolons
				#return;?
				elif next1 == '-' or next1 == '+':
					pass
					
				elif next1 == ';':
					next2 = getNext(nextObj['index'])
					#return;}?
					if next2 and next2 == '}':
						#delete next semicolon
						Main.data[count:next2['index']] = ['return']
				#return { or return (
				elif next1 == '{' or next1 == '(' or next1 == '[':
					skipSpace = True
					switch = '}' if next1 == '{' else ')'
					end = findTerminator(switch, next1, nextObj['index'])
					next2 = getNext(end)
					if next2 and isOpen(next2['value']):
						Main.data.insert(end + 1, ';3')
				#return .*
				elif next1 != 'function' and next1 != 'new':
					next2 = getNext(nextObj['index'])
					#TODO
					#TODO
					#TODO
					#print(next2)	
					#print(Main.data[next2['index']-5:next2['index']+5] )
					if next2 and isOpen(next2['value']) and next2['value'] != '?' and next2['value'] != '.':
						#return foo[bar] or return foo(bar)
						if next2['value'] == '[' or next2['value'] == '(':
							switch = ']' if next2['value'] == '[' else ')'
							end = findTerminator(switch, next2['value'], next2['index'])
							next3 = getNext(end)
							if next3 and isOpen(next3['value']):
								Main.data.insert(end + 1, ';2')						
						else:
							Main.data.insert(nextObj['index'] + 1, ';1')
			elif syntax == 'new':
				pass
				#nextObj = getNext(count)
				#print(nextObj)
			elif syntax == 'var':
				#seek 1, check for =
				next2 = getNext(count,1)
				if next2 and isOpen(next2['value']) and next2['value'] not in assignment:
					next1 = getNext(count)
					Main.data.insert(next1['index'] + 1, ';4') 

			#safety check void definition
			elif syntax == 'void':
				next2 = getNext(count)
				if not next2 or next2['value'] != '0':
					#skip zero
					Main.quit("Error parse 'void' not a valid reference")
			#finall check for spacing
			if Main.config.whitespace:
				if not skipSpace:
					#add space if not returning object
					Main.data.insert(count + 1, ' ')
				else: 
					skipSpace = False
		#if syntax == ';':
		#	next1 = getNext(count)
			#opt -- remove extra semicolons
			#if next1['value'] == '}':
			#		Main.data[count:next1['index']+1] = '}'

		elif syntax == 'case':
			nextObj = getNext(count)
			next1 = nextObj['value']
			#if not string
			if next1[0:3] != '@S_':
				end = findTerminator(':', False, nextObj['index'])
				Main.data[count : end] = ['case',' ', next1]
		elif syntax == 'if':
			#next1 = Main.get(count + 1)
			prevObj = getPrev(count)

			if prevObj and prevObj['value'] == 'else':
				if Main.config.whitespace:
					Main.data.insert(count, ' ')
				Main.skip += 1
		#elif syntax == 'else':
			#next1 = Main.get(count + 1)

		elif syntax == '=':
			#grab defined name
			if count == 0:
				Main.exit('File cannot begin with =')
			prev = getPrev(count)	
			if prev:
				name = prev['value']
				translation = Main.userVars.get(name)
				#if continued mathematical
				symbols = re.match(r'[\*\+\-><]', name)
				if translation == None and symbols == None:
					Main.userVars[name] = gen.alpha()
				elif symbols != None and name != '=':
					prev2 = getPrev(prev['index'])
					if prev2:
						Main.userVars[prev2['value']] = gen.alpha()
			else:
				raise IndexError(name)
		elif syntax == 'function':
			#grab defined function name
			nextObj = getNext(count)
			#is function call started: "function("
			if nextObj and nextObj['value'] != '(':
				next2 = getNext(nextObj['index'])		
				if not next2:
					raise IndexError('x11')
				else:
					name = next2['value']
					if not Main.userVars.get(name):
						Main.userVars[name] = gen.alpha()
		count += 1
	count = 0
	
	#Main.complete()
	#print(Main.data)

	defaults = {} if not Main.config.get('susbsitute') else Main.subsituteVars.copy()
	#end for
	for syntax in Main.data:
		if syntax in defaults:
			Main.data[count] = Main.userVars[syntax]
		#prev = Main.get(count - 1)
		elif syntax not in blocked:# and (not prev or prev != '/'):
			match = re.search(r'[@\w\$]+', syntax)
			if match != None:
				word = match.group(0)
				if word[0:3] == '@S_' and word in Main.userStrings:
					#string replace
					Main.data[count] = Main.userStrings[word]
					#replace each word
				elif word == '@_n':
					Main.data[count] = '' if Main.config.newlines else '\n'
				
				elif word in Main.userVars:
					#make sure it isn't part of an object
					prev = Main.get(count - 1)
					next1 = Main.get(count + 1)
					if (prev and prev != '.') and ((not next1) or (next1 != ':')):
						Main.data[count] = Main.userVars[word]
		#increase by one
		count += 1
	#final string!!!
	Main.data = ''.join(Main.data)

	#write to file
	if Main.config.get('writepath'):
		expandPath = os.path.abspath(Main.config.writepath)
		dirPath = os.path.dirname(expandPath)

		if not os.path.isdir(dirPath):
			if Main.isatty:
				createDirs = checkDirs(dirPath)
				if not Main.config.get('force'):
					answer = Main.console.raw_input('Create Directories[Yes/No]? > ').lower()
					if answer == 'yes' or answer == 'y':
						os.makedirs(createDirs)
				else:
					os.makedirs(createDirs)
			#not interactive
			elif not Main.config.get('force'):
				Main.quit('Directories don\'t exists: use command option -x to force creation')
		with open(expandPath, 'w') as fp:
			fp.write(Main.data)
		#update Main
		Main.stats.update({
			'originalPath'	: Main.config.writepath, 
			'compilePath'	: expandPath,
			'compileSize'	: os.path.getsize(expandPath)
			})
	else:
		#update Main
		Main.stats['compileSize'] = Main.data.__len__()

	origSize = int(os.path.getsize(Main.config.filepath) if not Main.config.string else Main.config.string.__len__())
	Main.stats['originalSize'] = origSize
	Main.stats['percent'] = int(round(100 / (float(Main.stats['originalSize']) / float((Main.stats['originalSize'] - Main.stats['compileSize'])))))
	#complete the clean
	Main.complete()


#check and display directories
def checkDirs(dirPath):
	sep = os.sep
	dirs = dirPath.split(sep)[1:]
	count = 0
	isDir = True
	path = sep + dirs[0]
	while os.path.isdir(path):
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

	
