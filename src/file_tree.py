
SEPARATOR = '/'
MODIFICATION_FIELD = 'etag'
FILENAME_FIELD = 'name'
IS_DIR_FIELD = 'is_directory'


class File(object):

    def __init__(self, path, modification_stamp=''):
        self.path = path
        self.modification_stamp = modification_stamp


class FileTree(File):

    def __init__(self, dav, path, modification_stamp=''):
        super(FileTree, self).__init__(path, modification_stamp)
        self.files = {}
        self.directories = {}
        self.dav = dav

    def populate(self):
        if not self.modification_stamp:
            root, resources_in_current_directory = self.dav.enhanced_list(self.path, include_root=True)
            self.modification_stamp = root[MODIFICATION_FIELD]
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
            modification_stamp = r[MODIFICATION_FIELD]
            path = self._full_path(name)
            if r[IS_DIR_FIELD]:
                directories[name] = FileTree(self.dav, path, modification_stamp)
            else:
                files[name] = File(path, modification_stamp)
        return directories, files

    def update(self, updated_modification_stamp=''):
        if not updated_modification_stamp:
            updated_modification_stamp = self.dav.info(self.path)[MODIFICATION_FIELD]

        if self.modification_stamp != updated_modification_stamp:
            updated_resources = self.dav.enhanced_list(self.path)
            directories, files = self._parse_response(updated_resources)

            self._update_files(files)
            self._update_directories(directories)

        else:
            for _, subtree in self.directories.items():
                subtree.update()

    def _update_files(self, new_files):
        for f in new_files:
            if f not in self.files:
                self.files[f] = new_files[f]
            elif self.files[f].modification_stamp != new_files[f].modification_stamp:
                self.files[f] = new_files[f]

        removed_files = [file for file in self.files if file not in new_files]
        for file in removed_files:
            del self.files[file]

    def _update_directories(self, updated_directory_list):
        removed_directories = [directory for directory in self.directories if directory not in updated_directory_list]
        for directory in removed_directories:
            del self.directories[directory]

        for d in updated_directory_list:
            if d not in self.directories:
                self.directories[d] = updated_directory_list[d]
                self.directories[d].populate()
            else:
                self.directories[d].update(updated_directory_list[d].modification_stamp)

    def all_files(self):
        all_files = [self.files[file].path for file in self.files]

        for directory in self.directories.values():
            all_files.extend(directory.all_files())

        return all_files

    # new - old
    def diff(self, old_file_tree):
        new_files = [files for files in self.files if files not in old_file_tree.files]
        removed_files = [files for files in old_file_tree.files if files not in self.files]

        own_directories = self.directories.keys()
        old_directories = old_file_tree.directories.keys()

        new_directories, still_existing_directories, removed_directories = categorize_directories(own_directories, old_directories)

        # Completly new directories
        files_of_new_directories = flatten_nested([self.directories[d].all_files() for d in new_directories])
        new_files.extend(files_of_new_directories)

        # Removed directories
        files_of_removed_directories = [file for directory in removed_directories for file in old_file_tree.directories[directory].all_files()]
        removed_files.extend(files_of_removed_directories)

        # Check subdirs for new files if directory has existed before
        nested_new_files = [files for d in still_existing_directories for files in self.directories[d].diff(old_file_tree.directories[d])]
        new_files.extend(nested_new_files)
        return new_files

    def _full_path(self, sub):
        return '{}{}'.format(self.path, sub)


def categorize_directories(new_directory_list, old_directory_list):
    new = []
    still_existing = []
    removed = [directory for directory in old_directory_list if directory not in new_directory_list]

    for directory in new_directory_list:
        if directory in old_directory_list:
            still_existing.append(directory)
        else:
            new.append(directory)

    return new, still_existing, removed


def flatten_nested(list):
    return [elem for sublist in list for elem in sublist]
