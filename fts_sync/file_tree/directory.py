from __future__ import absolute_import
from fts_sync.file_tree.file import File
from fts_sync.utils.path_util import remove_excluded

ETAG_FIELD = 'etag'
FILENAME_FIELD = 'name'
IS_DIR_FIELD = 'is_directory'
SIZE_FIELD = 'size'


class Directory(File):

    def __init__(self, dav, path, etag=''):
        super(Directory, self).__init__(path, etag)
        self.files = {}
        self.directories = {}
        self.dav = dav

    def __len__(self):
        return len(self.files) + sum(map(len, self.directories))

    def is_modified(self, same_file_from_old_sync):
        return True

    def populate(self, excluded_patterns=None):
        if not self.etag:
            root, resources_in_current_directory = self.dav.enhanced_list(self.path, include_root=True)
            self.etag = root[ETAG_FIELD]
        else:
            resources_in_current_directory = self.dav.enhanced_list(self.path)

        result = self._parse_response(resources_in_current_directory)
        self.directories, self.files = [remove_excluded(items, excluded_patterns) for items in result]

        for _, subtree in self.directories.items():
            subtree.populate()

    def _parse_response(self, resources):
        directories = {}
        files = {}
        for r in resources:
            name = r[FILENAME_FIELD]
            size = r[SIZE_FIELD]
            etag = r[ETAG_FIELD]
            path = self._full_path(name)
            if r[IS_DIR_FIELD]:
                directories[name] = Directory(self.dav, path, etag)
            else:
                files[name] = File(path, etag, size)
        return directories, files

    def all_files(self):
        all_files = [self.files[file] for file in self.files]

        for directory in self.directories.values():
            all_files.extend(directory.all_files())

        return all_files

    def _full_path(self, sub):
        return '{}{}'.format(self.path, sub)
