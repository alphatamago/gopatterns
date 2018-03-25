import unittest

from gopatterns.common import *
from utils.leelazero_utils import *

class LeelaZeroUtilsTestCase(unittest.TestCase):
    def test_get_version_from_player(self):
        self.assertEqual(get_version_from_player("Leela Zero 0.12 af9ce63c"),
                          "af9ce63c")
        self.assertEqual(get_version_from_player("Aurora 0.12 af9ce63c"),
                          "af9ce63c")
        self.assertTrue(get_version_from_player("Leela Zero 0.12") is None)
        self.assertTrue(get_version_from_player("Human") is None)


    def test_get_versions_from_line(self):        
        self.assertEqual(get_versions_from_line("PB[Leela Zero 0.12 af9ce63c]"),
                          ["af9ce63c"])
        self.assertEqual(get_versions_from_line("PW[Leela Zero 0.12 af9ce63c]"),
                          ["af9ce63c"])
        self.assertEqual(get_versions_from_line("PW[Human]"), [])
        self.assertEqual(get_versions_from_line("PB[Human]"), [])
