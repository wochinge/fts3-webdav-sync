from __future__ import absolute_import

import unittest
from fts_sync.file_tree.file import File
from fts_sync.utils.path_util import path_with_timestamp, name_with_timestamp

TEST_TAG = '1234'


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

if __name__ == '__main__':
    unittest.main()