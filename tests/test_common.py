import unittest

from gopatterns.common import *

class CommonUtilsTestCase(unittest.TestCase):
    def test_board_to_np(self):
        board = [['w',  'w', 'b'],
                 ['b',  'w', 'w']]
        self.assertTrue((board_to_np(board) == board).all())

        board = [['w',  None, 'b'],
                 [None, None, 'w']]
        expected_board = [['w',  EMPTY, 'b'],
                          [EMPTY, EMPTY, 'w']]
        board2 = board_to_np(board)
        self.assertFalse((board2 == board).all())
        self.assertTrue((board2 == expected_board).all())


    def test_board_to_string(self):
        board = [['w',  'w', 'b'],
                 ['b',  'w', 'w']]
        np_board = np.array(board)
        np_board_str = np_pattern_to_string(np_board)
        np_board2 = string_to_np_pattern(np_board_str)

        self.assertTrue((np_board == np_board2).all())
