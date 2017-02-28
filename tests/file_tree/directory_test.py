from __future__ import absolute_import
import unittest
from mock import MagicMock
import fts_sync.file_tree.directory as tree


def _file(name, modification, is_dir=False):
    return {
        tree.FILENAME_FIELD: name,
        tree.IS_DIR_FIELD: is_dir,
        tree.SIZE_FIELD: 100,
        tree.ETAG_FIELD: modification
    }


def _testdir_from_existing(existing, new_files):
    new_files_list = existing[1] + new_files
    return existing[0], new_files_list


def mocked_return(return_value, sub_directories=[], return_value_subdir=[]):
    def side_effect(path, include_root=False):
        if path == TEST_PATH:
            return return_value
        if path in sub_directories:
            return return_value_subdir
        return []
    return side_effect


def _populate_test_directory(side_effect):
    client = MagicMock()
    client.enhanced_list = MagicMock(side_effect=side_effect)
    directory = tree.Directory(client, TEST_PATH)
    directory.populate()

    client.enhanced_list.assert_any_call(TEST_PATH, include_root=True)
    return directory

TEST_PATH = 'root/'
TEST_SUBDIR1 = 'subdir1/'
TEST_SUBDIR2 = 'dasdasd/'
EMPTY_DIR = (_file(TEST_PATH, '123'), [])

DIR_1_FILE_NO_SUB_DIRS = _testdir_from_existing(
    EMPTY_DIR,
    [
        _file('1.html', '123')
    ]
)

DIR_3_FILE_NO_SUB_DIRS = _testdir_from_existing(
    DIR_1_FILE_NO_SUB_DIRS,
    [
        _file('.hidden', '312'),
        _file('blu.tar.gz', '323')
    ]
)

DIR_1_FILE_1_SUB_DIR = _testdir_from_existing(
    DIR_1_FILE_NO_SUB_DIRS,
    [
        _file(TEST_SUBDIR1, '1', True)
    ]
)

DIR_1_FILE_2_SUB_DIR = _testdir_from_existing(
    DIR_1_FILE_1_SUB_DIR,
    [
        _file(TEST_SUBDIR2, '1', True)
    ]
)

SUBDIR_WITH_1_FILE_AND_NO_SUBDIR = DIR_1_FILE_NO_SUB_DIRS[1]
SUBDIR_WITH_1_FILE_AND_1_SUBDIR = DIR_1_FILE_1_SUB_DIR[1]


class DirectoryTest(unittest.TestCase):

    def _assert_correct_population(self, directory, expected_nr_of_directories, expected_nr_of_files):
        self.assertEqual(len(directory.directories), expected_nr_of_directories)
        self.assertEqual(len(directory.files), expected_nr_of_files)

    def test_file_population_with_empty_dir(self):
        return_value = mocked_return(EMPTY_DIR)
        directory = _populate_test_directory(return_value)
        self._assert_correct_population(directory, 0, 0)

    def test_file_population_with_1file_and_without_directories(self):
        return_value = mocked_return(DIR_1_FILE_NO_SUB_DIRS)
        directory = _populate_test_directory(return_value)
        self._assert_correct_population(directory, 0, 1)

    def test_file_population_with_3files_and_without_directories(self):
        return_value = mocked_return(DIR_3_FILE_NO_SUB_DIRS)
        directory = _populate_test_directory(return_value)
        self._assert_correct_population(directory, 0, 3)

    def test_file_population_with_1file_and_1_directory(self):
        return_value = mocked_return(DIR_1_FILE_1_SUB_DIR, [TEST_PATH + TEST_SUBDIR1])
        directory = _populate_test_directory(return_value)
        self._assert_correct_population(directory, 1, 1)

    def test_file_population_with_1file_and_2_directories(self):
        return_value = mocked_return(DIR_1_FILE_2_SUB_DIR, [TEST_PATH + TEST_SUBDIR1, TEST_PATH + TEST_SUBDIR2])
        directory = _populate_test_directory(return_value)
        self._assert_correct_population(directory, 2, 1)

    def test_subdir_population(self):
        return_value = mocked_return(DIR_1_FILE_1_SUB_DIR, [TEST_PATH + TEST_SUBDIR1],
                                     SUBDIR_WITH_1_FILE_AND_NO_SUBDIR)
        directory = _populate_test_directory(return_value)
        self._assert_correct_population(directory, 1, 1)
        subdirectory = directory.directories[TEST_SUBDIR1]
        self._assert_correct_population(subdirectory, 0, 1)

    def test_subdir_population_with_further_subdir(self):
        subdir_path = TEST_PATH + TEST_SUBDIR1
        return_value = mocked_return(DIR_1_FILE_1_SUB_DIR, [subdir_path],
                                     SUBDIR_WITH_1_FILE_AND_1_SUBDIR)
        directory = _populate_test_directory(return_value)
        self._assert_correct_population(directory, 1, 1)
        subdirectory = directory.directories[TEST_SUBDIR1]
        self._assert_correct_population(subdirectory, 1, 1)


