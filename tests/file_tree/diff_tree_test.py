from __future__ import absolute_import
import unittest
from fts_sync.file_tree.directory import Directory
from fts_sync.file_tree.file import File
from fts_sync.file_tree.diff_tree import DiffedTree
import fts_sync.file_tree.status as status


def _create_tree(files, dirs, dir_status=status.EMPTY):
    directory = Directory(None, 'test', directory_status=dir_status)
    directory.files = files
    directory.directories = dirs
    return directory


def _files(base_path, list_of_name_modification_tuples):
    files = {}
    for name, modification_time in list_of_name_modification_tuples:
        files[name] = File(base_path + name, modification_time, modification_time)
    return files

EMPTY_TREE = _create_tree({}, {})


class DiffTreeTest(unittest.TestCase):

    def _assert_length(self, diff_tree, nr_of_new_files, nr_of_modified_files):
        self.assertEqual(len(diff_tree.new_files()), nr_of_new_files)
        self.assertEqual(len(diff_tree.modified_files()), nr_of_modified_files)

    def _assert_right_files(self, list_of_expected_paths, file_list):
        actual_paths = [f.path for f in file_list]
        for expected in list_of_expected_paths:
            self.assertIn(expected, actual_paths)

    def test_diffing_empty_trees(self):
        diffed = DiffedTree(EMPTY_TREE, EMPTY_TREE)
        self._assert_length(diffed, 0, 0)

    def test_nothing_new_or_modified(self):
        test_files = _files('/', [('index.html', '123')])
        tree = _create_tree(test_files, {})

        diffed = DiffedTree(tree, tree)
        self._assert_length(diffed, 0, 0)

    def test_new_file(self):
        test_files = _files('/', [('index.html', '123')])
        new_tree = _create_tree(test_files, {})

        diffed = DiffedTree(EMPTY_TREE, new_tree)
        self._assert_length(diffed, 1, 0)
        self._assert_right_files(['/index.html'], diffed.new_files())

    def test_several_new_files(self):
        test_files = _files('/', [('index.html', '123'), ('.hidden', '123')])
        new_tree = _create_tree(test_files, {})

        diffed = DiffedTree(EMPTY_TREE, new_tree)
        self._assert_length(diffed, 2, 0)
        self._assert_right_files(['/index.html', '/.hidden'], diffed.new_files())

    def test_new_file_in_subdir(self):
        test_files = _files('sub/', [('index.html', '123')])
        sub_tree = _create_tree(test_files, {}, status.NEW)

        root_tree = _create_tree([], {'sub/': sub_tree})

        diffed = DiffedTree(EMPTY_TREE, root_tree)
        self._assert_length(diffed, 1, 0)
        self._assert_right_files(['sub/index.html'], diffed.new_files())

    def test_modified_file(self):
        old_files = _files('/', [('index.html', '123')])
        new_files = _files('/', [('index.html', 'dasd')])
        old_tree = _create_tree(old_files, {})
        new_tree = _create_tree(new_files, {})

        diffed = DiffedTree(old_tree, new_tree)
        self._assert_length(diffed, 0, 1)
        self._assert_right_files(['/index.html'], diffed.modified_files())

    def test_several_modified_files(self):
        old_files = _files('/', [('index.html', '123'), ('.hidden', '2')])
        new_files = _files('/', [('index.html', 'dasd'), ('.hidden', 'das')])
        old_tree = _create_tree(old_files, {})
        new_tree = _create_tree(new_files, {})

        diffed = DiffedTree(old_tree, new_tree)
        self._assert_length(diffed, 0, 2)
        self._assert_right_files(['/index.html', '/.hidden'], diffed.modified_files())

    def test_modified_file_in_subdir(self):
        test_files = _files('sub/', [('index.html', '123')])
        modified_test_files = _files('sub/', [('index.html', 'dasd')])
        sub_tree = _create_tree(test_files, {})
        modified_sub_tree = _create_tree(modified_test_files, {})

        old_root = _create_tree([], {'sub/': sub_tree})
        new_root = _create_tree([], {'sub/': modified_sub_tree})

        diffed = DiffedTree(old_root, new_root)
        self._assert_length(diffed, 0, 1)
        self._assert_right_files(['sub/index.html'], diffed.modified_files())

