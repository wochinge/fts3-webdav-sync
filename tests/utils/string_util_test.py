from __future__ import absolute_import

import unittest
from fts_sync.utils.string_util import remove_quotes


class TestPathUtil(unittest.TestCase):

    def testRemovingOfSingleQuotes(self):
        actual = remove_quotes("'test'")

        self.assertEqual(actual, 'test')

    def testRemovingOfDoubleQuotes(self):
        actual = remove_quotes('"test"')

        self.assertEqual(actual, 'test')

    def testRemovingOfQuotesWithoutQuotes(self):
        actual = remove_quotes('test')

        self.assertEqual(actual, 'test')

