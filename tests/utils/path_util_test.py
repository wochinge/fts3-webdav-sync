from __future__ import absolute_import

import unittest
from fts_sync.file_tree.file import File
from fts_sync.utils.path_util import path_with_timestamp, name_with_timestamp, split_in_url_and_directory, remove_excluded

TEST_TAG = '1234'

TEST_FILES = {
    1: File('.hidden'),
    2: File('error.log'),
    3: File('sub/subsub/access.log'),
    4: File('dir'),
    5: File('a/dir/in/a/dir')
}


class TestPathUtil(unittest.TestCase):

    def _test_with_timestamp(self, path, expected_pattern, function):
        test_file = File(path, etag=TEST_TAG)
        expected = expected_pattern.format(TEST_TAG)
        actual = function(test_file)
        self.assertEqual(actual, expected)

    def _test_path_with_timestamp(self, path, expected_pattern):
        self._test_with_timestamp(path, expected_pattern, lambda f: path_with_timestamp(f))

    def _test_name_with_timestamp(self, name, expected_pattern):
        self._test_with_timestamp('x/y/c', expected_pattern, lambda f: name_with_timestamp(name, f))

    def test_path_with_timestamp_without_data_type(self):
        self._test_path_with_timestamp('path/x/file', 'path/x/file_({})')

    def test_path_with_timestamp_with_data_type(self):
        self._test_path_with_timestamp('path/x/file.html', 'path/x/file_({}).html')

    def test_path_with_timestamp_with_dot_data_type(self):
        self._test_path_with_timestamp('path/x/file.tar.gz', 'path/x/file_({}).tar.gz')

    def test_path_with_timestamp_with_hidden_file(self):
        self._test_path_with_timestamp('path/x/.hidden', 'path/x/.hidden_({})')

    def test_name_with_timestamp_without_data_type(self):
        self._test_name_with_timestamp('file', 'file_({})')

    def test_name_with_timestamp_with_data_type(self):
        self._test_name_with_timestamp('file.html', 'file_({}).html')

    def test_name_with_timestamp_with_dot_data_type(self):
        self._test_name_with_timestamp('file.tar.gz', 'file_({}).tar.gz')

    def test_name_with_timestamp_with_hidden_file(self):
        self._test_name_with_timestamp('.hidden', '.hidden_({})')

    def test_split_in_url_and_directory_without_dir(self):
        url = 'http://google.de/'
        expected = 'http://google.de/', ''
        self._assert_correct_split(url, expected)

    def _assert_correct_split(self, url, expected):
        actual = split_in_url_and_directory(url)
        self.assertEqual(actual, expected)

    def test_split_in_url_and_directory_with_dir(self):
        url = 'http://google.de/any/dir/'
        expected = 'http://google.de/', 'any/dir/'
        self._assert_correct_split(url, expected)

    def test_split_in_url_and_directory_without_trailing_slash(self):
        url = 'http://google.de'
        expected = 'http://google.de/', ''
        self._assert_correct_split(url, expected)

    def test_split_in_url_and_directory_with_dir_without_trailing_slash(self):
        url = 'http://google.de/test'
        expected = 'http://google.de/', 'test/'
        self._assert_correct_split(url, expected)

    def test_split_in_url_and_directory_with_invalid_url(self):
        url = ''
        self.assertRaises(ValueError, split_in_url_and_directory, url)

    def test_remove_excluded_none_matching(self):
        actual = remove_excluded(TEST_FILES, [])
        self.assertEqual(actual, TEST_FILES)

    def test_remove_excluded_matching_filename(self):
        self._assert_correct_excluded(['error.log'], ['error.log'])

    def _assert_correct_excluded(self, to_exclude, expected):
        actual = remove_excluded(TEST_FILES, to_exclude)
        self.assertTrue(len(actual) == len(TEST_FILES) - len(expected))
        for file_name in expected:
            self.assertNotIn(File(file_name), actual.values())

    def test_remove_excluded_in_subdir_matching_filename(self):
        self._assert_correct_excluded(['*/access.log'], ['sub/subsub/access.log'])

    def test_remove_excluded_file_type(self):
        self._assert_correct_excluded(['*.log'], ['sub/subsub/access.log', 'error.log'])

    def test_remove_excluded_subdir(self):
        self._assert_correct_excluded(['a/dir/in/*'], ['a/dir/in/a/dir'])

if __name__ == '__main__':
    unittest.main()