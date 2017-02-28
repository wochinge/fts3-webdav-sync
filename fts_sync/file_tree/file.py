from __future__ import absolute_import
import fts_sync.file_tree.status as status


class File(object):

    def __init__(self, path, etag='', size=0, file_status=status.EMPTY):
        self.path = path
        self.etag = etag
        self.size = size
        self.status = file_status

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.path == other.path
                and self.etag == other.etag
                and self.size == other.size
                and self.status == other.status
                )

    def __str__(self):
        return self.path

    def __repr__(self):
        return str(self)

    def is_modified(self, same_file_from_old_sync):
        # do not use modification time / etag as synced files always have a different modification time
        return self.size != same_file_from_old_sync.size

    def copy(self, new_status=status.EMPTY):
        return File(self.path, self.etag, self.size, new_status)