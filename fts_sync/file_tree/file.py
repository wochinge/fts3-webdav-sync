from __future__ import absolute_import
import fts_sync.file_tree.status as status


class File(object):

    def __init__(self, path, modification_time=0, etag='', size=0, file_status=status.EMPTY):
        self.path = path
        self.modification_time = modification_time
        self.etag = etag
        self.size = size
        self.status = file_status

    def __str__(self):
        return self.path

    def __repr__(self):
        return str(self)

    def is_modified(self, same_file_from_old_sync):
        return self.modification_time != same_file_from_old_sync.modification_time

    def copy(self, new_status=status.EMPTY):
        return File(self.path, self.modification_time, self.etag, self.size, new_status)