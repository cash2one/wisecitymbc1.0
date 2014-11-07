from django.core.files.uploadhandler import FileUploadHandler
from .uploadedfile import TemporaryUploadedFile

__all__ = ['SAETemporaryFileUploadHandler']

class SAETemporaryFileUploadHandler(FileUploadHandler):
	"""
	Upload handler that streams data into a temporary file.
	"""
	def __init__(self, *args, **kwargs):
		super(SAETemporaryFileUploadHandler, self).__init__(*args, **kwargs)

	def new_file(self, file_name, *args, **kwargs):
		"""
		Create the file object to append to as data is coming in.
		"""
		super(SAETemporaryFileUploadHandler, self).new_file(file_name, *args, **kwargs)
		self.file = TemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset)

	def receive_data_chunk(self, raw_data, start):
		self.file.write(raw_data)

	def file_complete(self, file_size):
		self.file.seek(0)
		self.file.size = file_size
		return self.file
