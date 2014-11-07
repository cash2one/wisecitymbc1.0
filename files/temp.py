from django.core.files.utils import FileProxyMixin
import tempfile
import os

__all__ = ['NamedTemporaryFile']

class NamedTemporaryFile(FileProxyMixin):
	"""
	Temporary file object constructor that works in Windows and supports
	reopening of the temporary file in windows.
	"""
	def __init__(self, mode='w+b', bufsize=-1, suffix='', prefix='',
			dir=None):
		name = tempfile.mktemp(suffix=suffix, prefix=prefix,
									  dir=dir)
		self.name = name
		self.file = open(name, mode, bufsize)
		self.close_called = False

	# Because close can be called during shutdown
	# we need to cache os.unlink and access it
	# as self.unlink only
	unlink = os.unlink

	def close(self):
		if not self.close_called:
			self.close_called = True
			try:
				self.file.close()
			except (OSError, IOError):
				pass
			try:
				self.unlink(self.name)
			except (OSError):
				pass

	def __del__(self):
		self.close()
