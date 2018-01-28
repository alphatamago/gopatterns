import unittest

from gopatterns.common import *
from gopatterns.indexer import *

class IndexTestCase(unittest.TestCase):
    def test_pattern_transformations(self):
        # The particular PatternIndex params are not relevant for this test.
        indexer = PatternIndex(3, 1, 1, 1, False)
        for board, expected_num_unique_tr in [
                ([[EMPTY]], 1),
                ([[WHITE]], 1),
                ([[BLACK]], 1),
                ([[EMPTY, EMPTY],
                  [EMPTY, EMPTY]], 1),                
                ([[WHITE, WHITE],
                  [WHITE, WHITE]], 1),                
                ([[BLACK, EMPTY],
                  [EMPTY, BLACK]], 2),
                ([[BLACK, EMPTY],
                  [EMPTY, EMPTY]], 4),
                ([[BLACK, EMPTY],
                  [EMPTY, WHITE]], 4)
                ]:
            pattern = board_to_np(board)
            trs = indexer.pattern_transformations_(pattern)
            unique_trs = set([np_pattern_to_string(tr) for tr in trs])
            if len(unique_trs) != expected_num_unique_tr:
                print(board, expected_num_unique_tr, unique_trs)
            self.assertEqual(len(unique_trs), expected_num_unique_tr)
