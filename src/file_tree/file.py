
import status

class File(object):

    def __init__(self, path, modification_time=0, etag='', size=0):
        self.path = path
        self.modification_time = modification_time
        self.etag = etag
        self.size = size
        self.status = status.EMPTY

    def __str__(self):
        return self.path

    def __repr__(self):
        return str(self)

    def is_modified(self, same_file_from_old_sync):
        return self.size != same_file_from_old_sync.size
