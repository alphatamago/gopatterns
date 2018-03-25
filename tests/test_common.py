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


    def test_get_game_date_from_text(self):
        self.assertEqual(get_game_date_from_text("2010-02-03").year, 2010)
        self.assertEqual(get_game_date_from_text("2010-2-03").year, 2010)
        self.assertEqual(get_game_date_from_text("2010-02-3").year, 2010)
        self.assertEqual(get_game_date_from_text("2010-2-3").year, 2010)
        self.assertEqual(get_game_date_from_text("year 2010").year, 2010)

        self.assertEqual(get_game_date_from_text("2010-00-00").year, 2010)

        self.assertEqual(get_game_date_from_text("2010/02/03").year, 2010)
        self.assertEqual(get_game_date_from_text("2010/2/3").year, 2010)

        self.assertEqual(get_game_date_from_text("2010-02-03",
                                                 "/usr/col/1999-02-03.sgf").year,
                         2010)
        
        self.assertEqual(get_game_date_from_text("201-02-03",
                                                 "/usr/col/1999-02-03.sgf").year,
                         1999)

        self.assertEqual(get_game_date_from_text("201"), None)

        self.assertEqual(get_game_date_from_text(""), None)
        self.assertEqual(get_game_date_from_text("", ""), None)
        self.assertEqual(get_game_date_from_text("", "201"), None)

        # It is too noisy to pick any 4 digists from pathname as a year, without
        # additional edge-case handling.
        self.assertEqual(get_game_date_from_text("", "2010"), None)

        self.assertEqual(get_game_date_from_text("1650").year, 1650)

        # TODO - we cannot parse years earlier than 1900, unless they have a
        # leading 0
        self.assertEqual(get_game_date_from_text("650"), None)

        # TODO - this needs fixed somehow, so we don't end up with year 23
        self.assertEqual(get_game_date_from_text("20023-01-06").year, 23)

        # TODO - fix this too
        self.assertEqual(get_game_date_from_text(
            "17th c.",
            "gogod\\0196-1699\\1600JSTP23.sgf"), None)

    def test_count_stones(self):
        pattern = """
        . . b
        w w .
        . . .
        = = =
        """
        self.assertEqual(count_stones(pattern), 3)
        self.assertEqual(count_stones_by_color(pattern, 'b'), 1)
        self.assertEqual(count_stones_by_color(pattern, 'w'), 2)
