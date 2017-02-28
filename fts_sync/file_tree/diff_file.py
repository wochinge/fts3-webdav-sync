from __future__ import absolute_import
from fts_sync.file_tree.file import File


class DiffedFile(File):

    def __init__(self, file, status):
        super(DiffedFile, self).__init__(file.path, file.etag, file.size)
        self.status = status


