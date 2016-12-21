
class FileDiff(object):

    def __init__(self, new=None, modified=None, deleted=None):
        self.new = []
        self.modified = []
        self.deleted = []

        if new:
            self.new = new
        if modified:
            self.modified = modified
        if deleted:
            self.deleted = deleted

    def __len__(self):
        return len(self.new) + len(self.modified)

    def __str__(self):
        return 'File Diff:\nNew Files:\n{}\nModified Files:\n{}\nRemoved Files:\n{}'.format(self.new, self.modified, self.deleted)

    def __repr__(self):
        return str(self)

    def extend(self, file_diff):
        self.new.extend(file_diff.new)
        self.modified.extend(file_diff.modified)
        self.deleted.extend(file_diff.deleted)

    def add_new_files(self, new_files):
        self.new.extend(new_files)

    def add_removed_files(self, removed_files):
        self.new.extend(removed_files)