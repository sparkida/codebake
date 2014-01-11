
from sys import platform

if not platform.startswith('linux'):
	print('\033[1;41m!!!DEV MODE--remove "not" :: using readline\033[1;m')
	import readline
else:
	print('\033[1;41m!!!DEV MODE--remove "not" :: using pyreadline\033[1;m')
	import pyreadline
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


