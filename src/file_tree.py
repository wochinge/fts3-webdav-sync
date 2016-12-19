
SEPARATOR = '/'
MODIFICATION_FIELD = 'etag'
FILENAME_FIELD = 'name'
IS_DIR_FIELD = 'is_directory'
SIZE_FIELD = 'size'


class File(object):

    def __init__(self, path, modification_stamp='', size=0):
        self.path = path
        self.modification_stamp = modification_stamp
        self.size = size


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
            size = r[SIZE_FIELD]
            modification_stamp = r[MODIFICATION_FIELD]
            path = self._full_path(name)
            if r[IS_DIR_FIELD]:
                directories[name] = FileTree(self.dav, path, modification_stamp)
            else:
                files[name] = File(path, modification_stamp, size)
        return directories, files

    def all_files(self):
        all_files = [self.files[file].path for file in self.files]

        for directory in self.directories.values():
            all_files.extend(directory.all_files())

        return all_files

    # new - old
    def diff(self, old_file_tree):
        new_files, modified_files, removed_files = categorize_files(self.files, old_file_tree.files)

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
        for existing in still_existing_directories:
            new_sub_files, modified_sub_files, removed_sub_files =  self.directories[existing].diff(old_file_tree.directories[existing])
            new_files.extend(new_sub_files)
            modified_files.extend(modified_sub_files)
            removed_files.extend(removed_sub_files)

        return new_files, modified_files, removed_files

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


def categorize_files(updated, old_files):
    new = []
    modified = []
    removed = [old_files[file].path for file in old_files if file not in updated]
    for file in updated:
        if file in old_files:
            if updated[file].size != old_files[file].size:
                modified.append(updated[file].path)
        else:
            new.append(updated[file].path)

    return new, modified, removed


def flatten_nested(list):
    return [elem for sublist in list for elem in sublist]
