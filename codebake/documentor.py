"""
Codebake
Clean CSS, HTML, and JavaScript Files
v1.3.0
Author: Nicholas Riley
"""

import re, sys, os
from jinja2 import Template


class ExampleModel:

    """ Build a new example dictionary object
    from an example string: @example
    """

    @staticmethod
    def change(match):
        feed = match.group(1)
        content = match.group(3)
        tail = match.group(4)
        commentType = '/*' if match.group(2) != '//' else '//'
        if commentType == '/*':
            lines = content.split('\n')
            lineAmount = len(lines)
            content = []
            count = 0
            for line in lines:
                match = re.match(r'([ \t]*)(.*)', line)
                mfeed = match.group(1)
                mcontent = match.group(2)
                if count == 0:
                    content.append('%s<span class="csComment">/* %s</span>' % (feed, mcontent))
                elif count+1 == lineAmount:
                    #newline with "-/"
                    if line.strip() == '':
                        content.append('%s<span class="csComment">*/</span>' % mfeed)
                    else:
                        content.append('%s<span class="csComment">* %s */</span>' % (mfeed, mcontent))
                else:
                    content.append('%s<span class="csComment">* %s</span>' % (mfeed, mcontent))
                count += 1
            return '\n'.join(content)
        return '%s<span class="csComment">%s%s</span>%s' % (feed, commentType, content, tail)
    
    @classmethod
    def get(cls, lines):
        #get ini
        lines = re.sub(r'(\s*)(/-)(.*?)(-/)', cls.change, lines, 0, re.MULTILINE | re.DOTALL)
        lines = re.sub(r'(\s*)(//)(.*?)(\n)', cls.change, lines)
        linesArray = lines.split('\n')
        lines = []
        for line in linesArray:
            lines.append(r'<li>%s</li>' % line)
        lines = '\n'.join(lines)
        lines = re.sub(r'( {4}|\t)', '<span class="csIndent"></span>', lines)
        return lines


class ParamModel:

    """ Build a new parameter dictionary object
    from a parameter string: @param
    """
    
    default = {
            'name': '',
            'type': [],
            'optional': 'False',
            'default': 'None',
            'desc': ''
            }

    validTypes = [
            'string',
            'str',
            'object',
            'function',
            'callback',
            'array',
            'number',
            'float',
            'integer',
            'int'
            ]

    @classmethod
    def get(cls, params):
        config = cls.default.copy()
        config['name'] = params[1]
        config['type'] = params[0]
        config['desc'] = params[2][1:].strip()
        match = re.match(r'\{(.*)\}', config['type'])
        config['type'] = []
        capture = match.group(1).split('|')
        #TODO - check if paramType in valid
        for paramType in capture:
            if '=' in paramType:
                values = paramType.split('=')
                config['optional'] = 'True'
                config['type'].append(values[0])
                config['default'] = values[1]
            else:
                config['type'].append(paramType)
        if len(config['type']) > 1:
            config['type'] = '|'.join(config['type'])
        return config
    

def resolve_path(path, pathexists = os.path.exists):
    assert os.path.isdir(path), 'Target directory must exist'
    orig_path = '%s/manifest' % path
    if pathexists('%s.json' % orig_path):
        count = 1
        while True:
            path = '%s-%d.json' % (orig_path, count)
            if pathexists(path):
                count += 1
            else:
                break
    else:
        path = '%s.json' % orig_path
    return path

class GenerateDoc(object):

    """ 
    Creates a new SpkMan, manual page 
    expects page dictionary
    """
    
    PageModel = {
            'namespace': 0,
            'global': 0,
            'instance': None,
            'example': [],
            'usage': [],
            'info': [],
            'param': [],
            'rel': None
            }

    regexList = {
            'get': r'/\*{2}[\s\n*]*(.*?(?<=\*/))',
            'replaceString': r'([\(|=](?:\s+)?)((?<!/)/[^*/\n\s].*?[^\\]/[igm]{0,3})|((?P<qt>[\'"]).*?(?<!\\)(?P=qt))|(([0-9]x[a-zA-Z0-9]+))|((?<![\w\$])([0-9]+\.?)+)'
            }

    def __init__(self, main):
        self.page = None
        writepath = main.config['writepath']
        manifest = os.path.abspath(writepath) if writepath else os.path.abspath('./')
        '''
        manifest = os.path.abspath(manifest)
        #TODO - add in automated strict versioning, as you 
        #generate the docs over existing manifests, the system
        #should default to the newest system, unless marked "-unstable"
        #the previous manifest should remain the same
        '''
        manifest = resolve_path(manifest)
        #print('Creating Manifest: %s' % manifest)
        #os.mkdir(manifest)
        self.manifest = manifest
        self.main = main
        with open('./codebake/templates/default.html', 'r') as fp:
            self.engine = Template(fp.read())
        self.generate()
        indexes = []
        count = 1
        for lines in main.man:
            index, page = self.buildPage(lines)
            indexes.append({'index': index, 'page': self.engine.render(page)})
        import json
        with open(self.manifest, 'w') as fp:
            fp.write(json.dumps(indexes))
        print('Data file created: %s' % self.manifest)

    def generate(self):

        """
        Initializes everything...
        """
        
        main = self.main
        config = main.config
        main.man = []
        addMan = main.man.append
        filepath = config['filepath']
        findman = re.compile(self.regexList['get'], re.MULTILINE | re.DOTALL)
        capturing = False
        page = {}
        addPage = page.update
        with open(filepath) as fp:
            for i, line in enumerate(fp):
                sline = line.strip()
                if sline == '':
                    continue
                if capturing:
                    if sline[:2] == '*/':
                        #print('closing capture')
                        capturing = False
                        if page != {}:
                            addMan(page)
                            page = {}
                            addPage = page.update
                        continue
                    #match: * a line beginning with an asterisk followed by a space and something
                    match = re.search(r'\*\s?(\s*.*)', line)
                    try:
                        line = match.group(1)
                        if line != '':
                            addPage({i: line})
                    except AttributeError, IndexError:
                        print('skipping line: %d' % i)
                        print(line)
                elif sline[0:4] == '/**':
                    capturing = True

    def buildPage(self, line):
        
        """build pages from parsed lines"""
        page = self.PageModel.copy()
        #page = OrderedDict()
        keys = sorted(line.keys())
        count = 0
        skip = 0
        linenum = 0

        for num in keys:
            if skip > 0:
                skip -= 1
                continue
            match = re.match(r'^@([a-zA-Z]+) *(.+)?', line[num])
            if match is None:
                #print('invalid match: '...)
                count += 1
                continue
            else:
                method = match.group(1)
                if method == 'namespace':
                    page[method] = 1

                elif method == 'global':
                    page[method] = 1

                elif method == 'author':
                    info = {'name': match.group(2)}
                    while True:
                        nextline = line[keys[count+1]]
                        if nextline[0] == '-':
                            count += 1
                            skip += 1
                            ident = nextline[1:].split(':',1)
                            info[ident[0]] = ident[1].strip()
                        else:
                            page[method] = info
                            break

                elif method == 'info':
                    desc = [match.group(2)]
                    doBreak = False
                    while True:
                        try:
                            nextline = line[keys[count+1]]
                            mark = nextline[0]
                            if mark == '@':
                                doBreak = True
                        except IndexError:
                            doBreak = True
                        if doBreak:
                            desc = '\n'.join(desc)
                            page['info'].append(desc)
                            doBreak = False
                            break
                        else:
                            count += 1
                            skip += 1
                            desc.append(nextline)

                elif method == 'usage':
                    match = match.group(2)
                    key, val = match.split(':', 1)
                    page['usage'].append({'name': key, 'desc': val.strip()})

                elif method == 'param':
                    #match = re.match(r'(([\w]+)\s(\{.*?\})\s(.*))', match.group(3))
                    match = match.group(2).split(' ', 2)
                    paramString = ParamModel.get(match)
                    page['param'].append(paramString)

                elif method == 'example':
                    title = match.group(2)
                    doBreak = False
                    desc = []
                    gutter = ['<ul class="gutter">']
                    linenum = 0
                    while True:
                        linenum += 1
                        gutter.append('<li>%s</li>' % linenum)
                        try:
                            nextline = line[keys[count+1]]
                            mark = nextline[0]
                            if mark == '@':
                                doBreak = True
                        except IndexError:
                            doBreak = True
                        if doBreak:
                            gutter.append('</ul>')
                            gutter = '\n'.join(gutter)
                            desc = re.sub(self.regexList['replaceString'], self.stringExchange, '\n'.join(desc))
                            desc = ExampleModel.get(desc)
                            desc = re.sub(r'@S_[0-9]+', self.stringFix, desc)
                            page['example'].append({'gutter': gutter, 'title': title, 'desc': desc})
                            doBreak = False
                            break
                        else:
                            count += 1
                            skip += 1
                            desc.append(nextline)
                else:
                    page[method] = match.group(2)

            count += 1
        index = {
            'name': page['name'],
            'global': page['global'],
            'namespace': page['namespace'],
            'instance': page['instance'],
            'examples': page['example'],
            'examples_title': [ x['title'] for x in page['example'] ],
            'rel': page['rel']
            }
        return (index, page)
    
    def stringFix(self, string):
        """replace strings swapped with stringExchange()"""
        return self.main.userStrings[string.group(0)]

    def stringExchange(self, string):
            """create and return reference to string"""
            #create an exchange reference
            main = self.main
            exchangeRef = '@S_%d' % main.exchangeCount
            main.exchangeCount += 1
            g2 = string.group(2)
            #add to user stored strings
            if g2:
                    main.userStrings[exchangeRef] = g2
                    return '%s%s' % (string.group(1), exchangeRef)
            else:
                    main.userStrings[exchangeRef] = string.group(0)
            return exchangeRef



