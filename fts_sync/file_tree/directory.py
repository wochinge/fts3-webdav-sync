from __future__ import absolute_import
from fts_sync.file_tree.file import File

ETAG_FIELD = 'etag'
FILENAME_FIELD = 'name'
IS_DIR_FIELD = 'is_directory'
SIZE_FIELD = 'size'


class Directory(File):

    def __init__(self, path, etag=''):
        super(Directory, self).__init__(path, etag)
        self.files = {}
        self.directories = {}

    def __len__(self):
        return len(self.files) + sum(map(len, self.directories))

    def is_modified(self, same_file_from_old_sync):
        return True

    def all_files(self):
        all_files = [self.files[file] for file in self.files]

        for directory in self.directories.values():
            all_files.extend(directory.all_files())

        return all_files

    def _full_path(self, sub):
        return '{}{}'.format(self.path, sub)
