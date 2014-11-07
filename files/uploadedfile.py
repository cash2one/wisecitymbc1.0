import os
from io import BytesIO

from django.conf import settings
from django.core.files.base import File
from files import temp as tempfile
from django.utils.encoding import force_str
from django.core.files.uploadedfile import UploadedFile

class TemporaryUploadedFile(UploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk).
    """
    def __init__(self, name, content_type, size, charset):
        if settings.FILE_UPLOAD_TEMP_DIR:
            file = tempfile.NamedTemporaryFile(suffix='.upload',
                dir=settings.FILE_UPLOAD_TEMP_DIR)
        else:
            file = tempfile.NamedTemporaryFile(suffix='.upload')
        super(TemporaryUploadedFile, self).__init__(file, name, content_type, size, charset)

    def temporary_file_path(self):
        """
        Returns the full path of this file.
        """
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except OSError as e:
            if e.errno != 2:
                # Means the file was moved or deleted before the tempfile
                # could unlink it.  Still sets self.file.close_called and
                # calls self.file.file.close() before the exception
                raise
