from __future__ import absolute_import


class File(object):

    def __init__(self, path, etag='', size=0):
        self.path = path
        self.etag = etag
        self.size = size

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
