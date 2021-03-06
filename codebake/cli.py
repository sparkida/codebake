# -*- coding: utf-8 -*-
from os import sys
if sys == 'nt':
    import pyreadline
import readline
from code import InteractiveConsole

class Console(InteractiveConsole):
    def __init__(self, locals=None, filename="<console>", histfile=(".history")):
        InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)
    
    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.clear_history()
                readline.read_history_file(histfile)
            except IOError:
                pass
            from atexit import register
            register(self.save_history, histfile)

    def save_history(self, histfile):
        try:
            readline.set_history_length(30)
            readline.write_history_file(histfile)
        except:
            pass


