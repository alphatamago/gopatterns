import numpy as np

EDGE = '='
BLACK = 'b'
WHITE = 'w'
EMPTY = '.'

# Chars used for swapping colors
# Must be different than BLACK and WHILTE!
WHITE_REPL = 'W'
BLACK_REPL = 'B'

ROW_SEP = '\n'

# Since each board location is a single character, we don't need a separator
CELL_SEP = ' '

def board_to_np(board_area):
    """
    Turns a list of lists of strings representation of a board into a numpy
    array representation.
    """
    result = np.array(board_area, dtype=np.str)
    # The initial board_area may contain None for empty, we deal with that here
    result[result=='None'] = EMPTY
    return result


def np_pattern_to_string(pattern, cell_sep=CELL_SEP, row_sep=ROW_SEP):
    """
    Turns a numpy array representation of a pattern to a string
    """
    return row_sep.join([cell_sep.join(pattern[r,:])
                         for r in range(pattern.shape[0])])


def string_to_np_pattern(pattern, cell_sep=CELL_SEP, row_sep=ROW_SEP):
    """
    Turns a string represntation of a pattern into a numpy array.
    This is the reverse of np_pattern_to_string.
    """
    return np.array([row.split(cell_sep) for row in pattern.split(row_sep)])
