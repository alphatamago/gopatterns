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

    def test_check_adjacent_check_adjacent_stones_outside_pattern_left(self):
        indexer = PatternIndex((9, 9),
                               1, 10,
                               2,
                               only_corners=True)
        board = np.zeros((19, 19), dtype=np.str)
        board.fill(EMPTY)
        row = 18
        col = 11
        board[row, col-1] = BLACK
        board[row, col] = WHITE        
        self.assertTrue(indexer.check_adjacent_stones_outside_pattern_(
            board, 8, 0,
            row, col))


    def test_check_adjacent_check_adjacent_stones_outside_pattern_down(self):
        indexer = PatternIndex((9, 9),
                               1, 10,
                               2,
                               only_corners=True)
        board = np.zeros((19, 19), dtype=np.str)
        board.fill(EMPTY)
        row = 10
        col = 18
        board[row - 1, col] = BLACK
        board[row, col] = WHITE        
        self.assertTrue(indexer.check_adjacent_stones_outside_pattern_(
            board, 0, 8,
            row, col))


    def test_check_adjacent_check_adjacent_stones_outside_pattern_up(self):
        indexer = PatternIndex((9, 9),
                               1, 10,
                               2,
                               only_corners=True)
        board = np.zeros((19, 19), dtype=np.str)
        board.fill(EMPTY)
        row = 8
        col = 18
        board[row + 1, col] = BLACK
        board[row, col] = WHITE        
        self.assertTrue(indexer.check_adjacent_stones_outside_pattern_(
            board, 8, 8,
            row, col))


    def test_check_adjacent_check_adjacent_stones_outside_pattern_right(self):
        indexer = PatternIndex((9, 9),
                               1, 10,
                               2,
                               only_corners=True)
        board = np.zeros((19, 19), dtype=np.str)
        board.fill(EMPTY)
        row = 18
        col = 9
        board[row, col+1] = BLACK
        board[row, col] = WHITE
        self.assertTrue(indexer.check_adjacent_stones_outside_pattern_(
            board, 8, 8,
            row, col))
