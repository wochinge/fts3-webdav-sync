from __future__ import absolute_import
from fts_sync.file_tree.directory import Directory
import fts_sync.file_tree.status as status
from fts_sync.utils.path_util import name_with_timestamp


class DiffedTree(Directory):

    def __init__(self, old_tree=None, new_tree=None):
        super(DiffedTree, self).__init__(new_tree.dav, new_tree.path, new_tree.modification_time, new_tree.etag,
                                        new_tree.status)
        if old_tree is None and new_tree:
            self.directories = new_tree.directories
            self.files = new_tree.files
        else:
            self._diff(old_tree, new_tree)

    def _diff(self, old, new):
        self.files = _categorize_files(new.files, old.files)
        self.directories, sub_directories_to_diff = _categorize_directories(new.directories, old.directories)

        for directory_key in sub_directories_to_diff:
            self.directories[directory_key] = DiffedTree(old.directories[directory_key], new.directories[directory_key])

    def new_files(self):
        return self.files_with_status(status.NEW)

    def files_with_status(self, selected_status):
        if selected_status != status.MODIFIED and self.status == selected_status:
            return self.all_files()
        else:
            files_with_status = [self.files[file] for file in self.files if self.files[file].status == selected_status]
            for directory_key in self.directories:
                files_with_status += self.directories[directory_key].files_with_status(selected_status)
            return files_with_status

    def removed_files(self):
        return self.files_with_status(status.REMOVED)

    def modified_files(self):
        return self.files_with_status(status.MODIFIED)


def _categorize_files(new_files, old_files):
    return _categorize(new_files, old_files, False)[0]


def _categorize_directories(new_directories, old_directories):
    return _categorize(new_directories, old_directories, True)


def _categorize(new_files, old_files, is_directory):
    all_changed = {}
    modified = []

    for file_key in old_files:
        if file_key not in new_files:
            file = old_files[file_key]
            all_changed[file_key] = file.copy(status.REMOVED)

    for file_key in new_files:
        file = new_files[file_key]
        if file_key in old_files:
            if file.is_modified(old_files[file_key]) and name_with_timestamp(file_key, file) not in old_files:
                modified.append(file_key)
                all_changed[file_key] = file.copy(status.MODIFIED)
        else:
            copy = file.copy(status.NEW)
            all_changed[file_key] = DiffedTree(new_tree=copy) if is_directory else copy

    return all_changed, modified
