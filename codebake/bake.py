"""
Codebake
Clean CSS, HTML, and JavaScript Files
v1.3.2
Author: Nicholas Riley
"""

import re
from os import path, sep, makedirs

__version__ = '1.3.2'

class Generator(object):
        
    """
    Provides key creation and obfuscation values
    """

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
        self.used = set()
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
        #recursively return character
        if char in self.used:
            return self.alpha()
        self.used.add(char)
        return char
                    

def BakeHTML(Main):
    
    """
    Optimize HTML and inline CSS and JS from file or string

    options:
    closeGaps
    removeLineComments
    removeDocComments
    chunk - 1=1 rule per line
    strip
    """

    from oven import RecurseBake
    config = Main.config
    filepath = config['filepath']
    regexList = {
                    'extractJS':        r'(<script[^>]*?>)(.*?)(</script>)',
                    'extractCSS':       r'(<style[^>]*?>)(.*?)(</style>)',
                    'squeeze':          r'(\r?\n)+|\t|\s(\s)+'
            }

    #build regex commands
    searchJS = re.compile(r'%s' % regexList['extractJS'], re.MULTILINE | re.DOTALL)
    searchCSS = re.compile(r'%s' % regexList['extractCSS'], re.MULTILINE | re.DOTALL)
            

    def extractJS(string):
        head = string.group(1)
        tail = string.group(3)
        baker = RecurseBake(string.group(2))
        #bake it
        BakeJS(baker)
        mark = '[@__CODEBAKE__%d__XbnsjZOL224]' % Main.count
        Main.count += 1
        Main.userStrings[mark] = '%s%s%s' % (head, baker.data, tail)
        return mark

    def extractCSS(string):
        head = string.group(1)
        tail = string.group(3)
        baker = RecurseBake(string.group(2))
        #bake it
        BakeCSS(baker)
        mark = '[@__CODEBAKE__%d__XbnsjZOL224]' % Main.count
        Main.count += 1
        Main.userStrings[mark] = '%s%s%s' % (head, baker.data, tail)
        return mark


    #read file if not string
    if 'string' not in config:
        #get file from arg
        with open(filepath) as fp:
            Main.data = re.sub(regexList['squeeze'], '',
                    searchCSS.sub(extractCSS, searchJS.sub(extractJS, fp.read())))
    else:
        Main.data = re.sub(regexList['squeeze'], '',
                searchCSS.sub(extractCSS, searchJS.sub(extractJS, config['string'])))
    
    #replace stored Bakes
    marks = Main.userStrings
    for m in marks:
        Main.data = Main.data.replace(m, marks[m])
    #end
    Main.complete()



def BakeCSS(Main):
    
    """
    Optimize a CSS file or string

    options:
    closeGaps
    trimSemiColons
    removeLineComments
    removeDocComments
    chunk - 1=1 rule per line
    strip
    """
    
    config = Main.config
    filepath = config['filepath']
    chunkSize = config['chunk']
    regexList = {
            'removeLineComments'        : r'([\h\t]*/{2}.*[\r\n]?)',
            'removeDocComments'         : r'(/\*.*?(?<=\*/))',
            'closeGaps'                 : r'([\w\]\*]\s+{)',
            'strip'                     : r'([{:,;]\s+[.#\'"\w])',
            'trimSemiColons'            : r'(;(\s+)?})'
            }
    #build regex commands
    regexMulti = re.compile(r'%s' % regexList['removeDocComments'], re.MULTILINE | re.DOTALL)
    sub = re.sub
    #read file if not string
    if 'string' not in config:
        #get file from arg
        with open(filepath) as fp:
            Main.data = regexMulti.sub('', fp.read())
    else:
        Main.data = regexMulti.sub('', config['string'])

    def chunk(string):
        if config['chunk'] == Main.chunkCount:
            Main.chunkCount = 1
            return '\n'
        Main.chunkCount += 1

    def trim(string):
        seg = string.group(0)
        return '%s%s' % (seg[0], seg[-1])

    def trimLeft(string):
        seg = string.group(0)
        return seg[-1]

    if chunkSize > 0:
        if chunkSize > 1:
            Main.data = sub('\n', chunk, Main.data)
        else:
            Main.data = sub('}', '}\n', sub('\n', '', Main.data))
    else:
        Main.data = sub('\n', '', Main.data)
    #remove line comments and dbg statements
    Main.data = sub(regexList['strip'], trim,
           sub(regexList['trimSemiColons'], trimLeft,
           sub(regexList['closeGaps'], trim,
           sub(regexList['removeLineComments'], '', Main.data.strip()))))
    Main.complete()


def BakeJS(Main):

    """
    Optimize a CSS file or string

    options:
    removeLineComments
    removeDocComments
    chunk
    obfuscate
    subsitute
    """



    config = Main.config
    subsitute = config['subsitute']
    obfuscate = config['obfuscate']
    filepath = config['filepath']
    header = None
    
    '''
    ***DEP***
    if subsitute:
        for n in Main.subsituteVars.copy():
            addVar(n)
            userVarsFreq[n] += 1
    '''
    from collections import defaultdict
    gen = Generator()   
    genAlpha = gen.alpha
    userVars = Main.userVars = defaultdict(int)
    subsituteVars = Main.subsituteVars
    regexList = {
            'removeFunctionCalls'       : r'((?:%s)\(.*\)[,\|;]?)',
            'removeLineComments'        : r'([\h\t]*/{2}.*[\r\n]?)',
            'removeDocComments'         : r'(/\*.+?\*/)',
            'replaceString'             : r'([\(|=](?:\s+)?)((?<!/)/[^*/\n\s].*?[^\\]/[igm]{0,3})|((?P<qt>[\'"]).*?(?<!\\)(?P=qt))|(([0-9]x[a-zA-Z0-9]+))|((?<![\w\$])([0-9]+\.?)+)'
            }



    #build regex commands
    stripx = config['stripx']
    if stripx:
        stripx = '|'.join([ x.strip() for x in stripx.split(',') ])
        regex = '%s|%s' % (regexList['removeLineComments'], (regexList['removeFunctionCalls'] % stripx))
    else:
        regex = regexList['removeLineComments']
    regexMulti = re.compile(regexList['removeDocComments'], re.MULTILINE | re.DOTALL)
    
    def stringExchange(string):
        """create and return reference to string"""
        #create an exchange reference
        exchangeRef = '@S_%d' % Main.exchangeCount
        Main.exchangeCount += 1
        g2 = string.group(2)
        #add to user stored strings
        if g2:
            Main.userStrings[exchangeRef] = g2
            return '%s%s' % (string.group(1), exchangeRef)
        else:
            Main.userStrings[exchangeRef] = string.group(0)
        return exchangeRef

    def functionCapture(string):
        """capture 'function(.*)' parameters and define as vars, will follow"""
        match = re.sub(r'[^\w]',' \r',string.group(1)).split()
        if len(match):
            for name in match:
                userVars[name] += 1
        return string.group(0)
    
    def chunk(string):
        if config['chunk'] == Main.chunkCount:
            Main.chunkCount = 1
            return ' @_n '
        Main.chunkCount += 1

    #read file if not string
    if 'string' not in config:
        #get file from arg
        with open(filepath) as fp:
            Main.data = fp.read()
    else:
        Main.data = config['string']

    
    '''
    reg = re.compile(r'', re.MULTILINE | re.DOTALL)
    reg.sub(exchangeTernary
    return
    '''
    
    if config['saveHeader']:
        regexMulti = re.compile(regexList['removeDocComments'], re.MULTILINE | re.DOTALL)
        match = regexMulti.search(Main.data)
        if match:
            header = re.sub(r'\s(\s)+', ' ', match.group(0))

    #replace strings, remove comments and stripx
    Main.data = re.sub(regex, '', 
        regexMulti.sub('', 
        re.sub(regexList['replaceString'], stringExchange, Main.data)))

    if obfuscate:
        Main.data = re.sub(r'function\((.*?\))', functionCapture, Main.data)
    

            
    '''
    #strip whitespace !only when strict
    if not Main.config['whitespace']:
            Main.data = re.sub(' ', ' @_s ', Main.data)
            Main.data = re.sub('\t', ' @_t ', Main.data)
    '''
    
    if config['chunk']:
        Main.data = re.sub('\n', chunk, Main.data)
    #mark characters, seperate by anything that isn't valid character
    Main.data = re.sub(r'([^\w\d_@$])', r' \1 ', Main.data).split()
    #read string data
    spaceRequired = [
            'void',
            'new',
            'var',
            'typeof',
            'throw',
            #'return',
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

    blocked = set(spaceRequired + dualSpaceRequired + Generator.block + blockList)
    defaults = {} if not subsitute else Main.subsituteVars.copy()
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
                    self.value = Main.data[self.index]
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
                    try:
                        self.value = Main.data[self.index]
                    except IndexError:
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
    mget = Main.get
    insert = Main.data.insert
    seekprev = seek['prev']
    seeknext = seek['next']
    
    def obfuscateAdd(index):    
        """add main data value from index, to obfuscate list"""
        if obfuscate:
            value = Main.data[index]
            if value in blocked:
                return
            seekprev(index)
            prev = seekprev.value
            #make sure it isn't part of an object
            #if it is a ternary then obfuscate
            if prev and prev != '.':
                seeknext(index)
                next1 = seeknext.value
                if not next1 or next1 != ':' or prev == '?':
                    userVars[value] += 1


    for syntax in Main.data:
        if Main.skip > 0:
            Main.skip -= 1
            count += 1
            continue
        if syntax[0] == '@':
            _syntax3 = syntax[0:3]
            if _syntax3 == '@S_':
                Main.data[count] = Main.userStrings[syntax]
            elif config['chunk']:
                if _syntax3 == '@_n':
                    Main.data[count] = '\n'
                elif _syntax3 == '@_t':
                    Main.data[count] = '\t'
                elif _syntax3 == '@_s':
                    Main.data[count] = ' '
            count += 1
            continue
        elif syntax == '=':
            if obfuscate:
                #== , != , /= , += ,-=
                dist = 0
                skip = defName = False
                while count - (dist + 1) > 0:
                    dist += 1
                    defName = Main.data[count - dist]
                    #print('%s\t%s' % (syntax, defName))
                    if defName[0:3] == '@S_':
                        skip = True
                        break
                    if defName == ' ' or defName == '\n':
                        break
                    if defName not in operators and defName not in skipChars:
                        break
                if skip or not defName:
                    continue
                obfuscateAdd(count - dist)
        elif syntax != '=' and syntax != ';' and (syntax[0:1] in operators or syntax[0:1] in skipChars):
            count += 1
            continue
        elif subsitute and syntax in defaults:
            Main.data[count] = subsituteVars[syntax]
        elif syntax in dualSpaceRequired:
            insert(count, ' ')
            insert(count + 2, ' ')
            Main.skip += 2
        else:
            seeknext(count)
            next1 = seeknext.value
            if not next1:
                break
            if next1 == ';' or next1 == ',':
                #spare the seek if we can
                seekprev(count)
                prev1 = seekprev.value
                if prev1 == ',':
                    userVars[syntax] += 1
            elif ';' == syntax:
                #opt -- remove extra semicolons
                if config['extras'] and next1 == '}':
                    Main.data[count:seeknext.index + 1] = ['}']
            elif 'else' == syntax:
                if next1 != '{':
                    insert(count+1, ' ')
                    Main.skip += 1
            elif 'function' == syntax:
                if next1 and next1 != '(':
                    #set name
                    obfuscateAdd(seeknext.index)
                    insert(count + 1, ' ')
                    Main.skip += 1
            elif 'return' == syntax:
                if '}' != next1:
                    insert(count + 1, ' ')
                    #and skip all
                    Main.skip += 1
            elif 'case' == syntax:
                #if not string
                if next1[0:3] != '@S_' or Main.userStrings[next1].isdigit():
                    insert(count + 1, ' ')
                    Main.skip += 1
            elif syntax in spaceRequired:
                insert(count + 1, ' ')
                #and skip all
                Main.skip += 1
        count += 1

    if obfuscate:
        '''
        create a defaultdict that starts a set
        which we'll use to keep an index of items
        to be obfuscated. We will then be able to 
        calculate the total size of the indexes
        (all the indexes of a single set added up),
        so if we had an index 'myValue' with set([0, 2, 18, 34])
        we would calculate 'myValue'.__len__() * len(set)
        as opposed to prioritizing the largest set(amount of indexes)
        '''
        exchangeVar = defaultdict(set)
        count = 0
        skipChars.update([';','\n'] + list(operators))
        blocked = set(list(blockList) + ['case','new', 'void 0', 'if', 'else'] + list(dualSpaceRequired) + list(spaceRequired) + defaults.values())
        for syntax in Main.data:
            if syntax.isdigit() or syntax[0:1] in skipChars or syntax in blocked:
                count += 1
                continue
                if syntax in userVars:
                    dist = 0
                    while True:
                        dist += 1
                        prev = Main.data[count - dist]
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
                        if next1 != ':' or prev == '?':
                            exchangeVar[syntax].add(count)
                        elif next1 == ':':
                            if prev == ',' or prev == '{':
                                pass
                            else:
                                exchangeVar[syntax].add(count)
                count += 1
        #set optimal vars
        userVarsFreq = [ (len(v) * k.__len__(), k) for k,v in exchangeVar.iteritems() ] 
        userVarsFreq.sort(reverse=True)
        for v,k in userVarsFreq:
            exchange = genAlpha()
            for pointer in exchangeVar[k]:
                Main.data[pointer] = exchange
    #save the header!
    if config['saveHeader'] and header:
        Main.data.insert(0, header)
    #final string!!!
    Main.data = ''.join(Main.data)
    
    #write to file
    if config['writepath']:
        outputPath = Main.stats['outputPath'] = path.abspath(config['writepath'])
        dirPath = path.dirname(outputPath)
        if not path.isdir(dirPath):
            if Main.isatty:
                createDirs = checkDirs(dirPath)
                if not config['force']:
                    answer = raw_input('Create Directories[Yes/No]? > ').lower()
                    if answer == 'yes' or answer == 'y':
                        makedirs(createDirs)
                else:
                    makedirs(createDirs)
            #not interactive
            elif not config['force']:
                Main.quit('Directories don\'t exists: use command option -x to force creation')
        with open(outputPath, 'w') as fp:
            fp.write(Main.data)
        #update Main
        if config['verbose']:
            Main.stats['originalPath'] = config['writepath']
            Main.stats['compileSize'] = path.getsize(outputPath)
    elif config['verbose']:
        #update Main
        Main.stats['compileSize'] = Main.data.__len__()
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
    join = path.join
    relPath = path.splitdrive(dirPath)[1]
    dirs = relPath.split(sep)
    if dirs[0] == '':
        dirs = dirs[1:]
    fullpath = '%s%s' % (sep, dirs.pop(0))
    while True:
        fullpath = join(fullpath, dirs.pop(0))
        if not path.isdir(fullpath):
            break
    print("------------------\nDirectories don't exist:")
    for d in dirs:
        fullpath = join(fullpath, d)
        print(fullpath)
    return fullpath

    
