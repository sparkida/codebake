Codebake
========
The fastest and most reliable JS, CSS and HTML optimizer around.

Features
--------
* **Strip** - Codebake automatically strips doc and inline comments as well as extra whitespace characters: space, tab, newline (This will be made optional in next release update **v1.4**)
* **Chunking** - A really useful feature for developers: **Chunking** expedites debugging JavaScript and can neatly structure CSS files to be more readable by adding line breaks every "**x**" amount of steps, otherwise all baked code is returned in a single line, and there is no efficient way to hunt down JS errors.
* **Obfuscate** - When baking JavaScript files, obfuscation helps to reduce size (average 20-40%) and eliminates readability, ideal for production environments.
* **Extras** - Whether baking JavaScript or CSS files, the **extras** feature will remove any unneccessary semicolons and commas.
* **Recipes** - Codebake will process a Manifest like file called a "*recipe*". Recipe files are very basic:
```
#start by defining the format to use
[js]
#then list your files in the desired order, excluding extensions
#so if we had files: "head.js, body.js, tail.js"
head
body
tail
#presto!
```

Requirements
------------
* Python 2.6, 2.7
* Linux / Windows / Mac OS X
* **Make sure** you have the latestst version of [pip](http://pip.readthedocs.org/en/latest/installing.html)
* **Make sure** you have the latest version of [setuptools](https://pypi.python.org/pypi/setuptools#installation-instructions)

Get
---
Download or clone this repository

**Download:**
[codebake-master.zip](https://github.com/sparkida/codebake/archive/master.zip)

**Clone:**
```
#https
git clone https://github.com/sparkida/codebake
#ssh
git clone git@github.com:sparkida/codebake
```

Install
-------

**Important**: be sure the codebake directory is the parent
directory of the package containing a setup.py file
```
pip install ./codebake
```


Once Installed
--------------
1. Type "**bake**"
2. Have fun!








