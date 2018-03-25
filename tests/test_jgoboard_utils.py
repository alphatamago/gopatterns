import unittest

from utils.jgoboard_utils import process_pattern_for_jgoboard

class JgobatUtilsTestCase(unittest.TestCase):
    def test_process_pattern_for_jgoboard(self):
        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
         """ 
        = w .  
        = . . 
        = = = 
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 2, 'B', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """ 
        =. . . . . . . 
        =. . . . . b . 
        =. . . . w b w 
        =. . . w b w . 
        =. . . b b w .  
        =. . . . . . . 
        = = = = = = = =
        """
        )
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 6, 'G', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        =. . . . . . . . . 
        =. . . . . . . . . 
        =. . . . . . . . . 
        =. . . . . . . . . 
        =. . . . . b . . . 
        =. . . . w b w . . 
        =. . . w b w . . . 
        =. . . b b w . . . 
        =. . . . . . . . . 
        = = = = = = = = = =
        """
        )
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 9, 'J', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        . . =
        b . =
        = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('S', 2, 'T', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . b . . . =
        . . . . w b w . . =
        . . . w b w . . . =
        . . . b b w . . . =
        . . . . . . . . . =
        = = = = = = = = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('L', 9, 'T', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
         """
        = = =
        . w =
        b . =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('S', 19, 'T', 18))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = = = = = = = =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . b . . . =
        . . . . w b w . . =
        . . . w b w . . . =
        . . . b b w . . . =
        . . . . . . . . . =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('L', 19, 'T', 11))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = =
        = b . 
        = . . 
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 19, 'B', 18))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = = = = = = = =
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . b . . . 
        = . . . . w b w . . 
        = . . . w b w . . . 
        = . . . b b w . . . 
        = . . . . . . . . . 
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 19, 'J', 11))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = =
        = . . = 
        = . . =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 19, 'B', 18))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = = = = = = = = = = = = = = = = = = =
        = . . . . . . . . . . . . . . . . . b . = 
        = . . . . . . . . . . . . . . . . . w . =""")
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 19, 'T', 18))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = . . = 
        = . . =
        = = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 2, 'B', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = . . . . . . . . . . . . . . . . . b . = 
        = . . . . . . . . . . . . . . . . . w . =
        = = = = = = = = = = = = = = = = = = = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 2, 'T', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = =
        = . .
        = . .
        = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 2, 'B', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = = = = = = = =
        = . . . . . . . . .
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . b . . . 
        = . . . . w b w . . 
        = . . . w b w . . . 
        = . . . b b w . . . 
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . . . . . 
        = . . . . . b . . . 
        = . . . . w b w . . 
        = . . . w b w . . . 
        = . . . b b w . . . 
        = . . . . . . . . . 
        = = = = = = = = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 19, 'J', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = =
        . . = 
        . . =
        = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('S', 2, 'T', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = = = = = = = =
        . . . . . . . . . =
        . . . . . . . . . = 
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . b . . . =
        . . . . w b w . . =
        . . . w b w . . . =
        . . . b b w . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . . . . . =
        . . . . . b . . . =
        . . . . w b w . . =
        . . . w b w . . . =
        . . . b b w . . . =
        . . . . . . . . . =
        = = = = = = = = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('L', 19, 'T', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = =
        = . . = 
        = . . =
        = = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 2, 'B', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = = = = = = = = = = = =
        = . . . . . . . . . . . . = 
        = . . . . . . . . . . . . =
        = = = = = = = = = = = = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 2, 'M', 1))

        _, _, _, left_col, upper_row, right_col, lower_row = process_pattern_for_jgoboard(
        """
        = = = = = = = = = = =
        = . . . . . . . . . =
        = . . . . . . . . . = 
        = . . . . . . . . . =
        = . . . . . . . . . =
        = . . . . . . . . . =
        = . . . . . . . . . =
        = . . . . . . . . . =
        = . . . . . b . . . =
        = . . . . w b w . . =
        = . . . w b w . . . =
        = . . . b b w . . . =
        = . . . . . . . . . =
        = . . . . . . . . . =
        = . . . . . . . . . =
        = . . . . . b . . . =
        = . . . . w b w . . =
        = . . . w b w . . . =
        = . . . b b w . . . =
        = . . . . . . . . . =
        = = = = = = = = = = =
        """)
        self.assertEqual((left_col, upper_row, right_col, lower_row),
                         ('A', 19, 'J', 1))
