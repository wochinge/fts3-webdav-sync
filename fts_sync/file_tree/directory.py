
from file import File
import status
from fts_sync.utils.path_util import name_with_timestamp

MODIFICATION_TIMESTAMP_FIELD = 'modified'
ETAG_FIELD = 'etag'
FILENAME_FIELD = 'name'
IS_DIR_FIELD = 'is_directory'
SIZE_FIELD = 'size'


class Directory(File):

    def __init__(self, dav, path, modification_time=0, etag=''):
        super(Directory, self).__init__(path, modification_time, etag)
        self.files = {}
        self.directories = {}
        self.dav = dav

    def __len__(self):
        return len(self.files) + sum(map(len, self.directories))

    def is_modified(self, same_file_from_old_sync):
        return True

    def populate(self):
        if not self.etag:
            root, resources_in_current_directory = self.dav.enhanced_list(self.path, include_root=True)
            self.modification_time = root[MODIFICATION_TIMESTAMP_FIELD]
            self.etag = root[ETAG_FIELD]
        else:
            resources_in_current_directory = self.dav.enhanced_list(self.path)
        self.directories, self.files = self._parse_response(resources_in_current_directory)

        for _, subtree in self.directories.items():
            subtree.populate()

    def _parse_response(self, resources):
        directories = {}
        files = {}
        for r in resources:
            name = r[FILENAME_FIELD]
            size = r[SIZE_FIELD]
            etag = r[ETAG_FIELD]
            modification_stamp = r[MODIFICATION_TIMESTAMP_FIELD]
            path = self._full_path(name)
            if r[IS_DIR_FIELD]:
                directories[name] = Directory(self.dav, path, modification_stamp, etag)
            else:
                files[name] = File(path, modification_stamp, etag, size)
        return directories, files

    def all_files(self):
        all_files = [self.files[file] for file in self.files]

        for directory in self.directories.values():
            all_files.extend(directory.all_files())

        return all_files

    def new_files(self):
        return self.files_with_status(status.NEW)

    def files_with_status(self, selected_status):
        if selected_status != status.MODIFIED and self.status == status:
            return self.all_files()
        else:
            files_with_status = [self.files[file] for file in self.files if self.files[file].status == selected_status]
            for directory_key in self.directories:
                files_with_status += self.directories[directory_key].files_with_status(status)
            return files_with_status

    def removed_files(self):
        return self.files_with_status(status.REMOVED)

    def modified_files(self):
        return self.files_with_status(status.MODIFIED)

    def _full_path(self, sub):
        return '{}{}'.format(self.path, sub)

    def diff_tree(self, old):
        current = Directory(self.path, self.modification_time, self.etag)
        current.files = _categorize(self.files, old.files)[0]

        current.directories, sub_directories_to_diff = _categorize(self.directories, old.directories)
        for directory_key in sub_directories_to_diff:
            current.directories[directory_key] = self.directories[directory_key].diff_tree(old.directories[directory_key])

        return current

    def changed_files(self, old_files):
        return [self.files[changed] for changed in self.files if changed in old_files and self.files[changed].is_modified(file, old_files)]


def _categorize(new_files, old_files):
    all_changed = {}
    modified = []

    for file_key in old_files:
        if file_key not in new_files:
            file = old_files[file_key]
            file.status = status.REMOVED
            all_changed[file_key] = file

    for file_key in new_files:
        file = new_files[file_key]
        if file_key in old_files:
            if file.is_modified(old_files[file_key]) and name_with_timestamp(file_key, file) not in old_files:
                file.status = status.MODIFIED # does not matter for directories
                modified.append(file_key)
                all_changed[file_key] = file
        else:
            file.status = status.NEW
            all_changed[file_key] = file

    return all_changed, modified