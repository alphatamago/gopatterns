from datetime import datetime
import re
import sys

import numpy as np
import pandas as pd

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

date_pattern1 = re.compile('\d\d\d\d-(\d)?\d-(\d)?\d')
date_pattern2 = re.compile('\d\d\d\d/(\d)?\d/(\d)?\d')
date_pattern3 = re.compile('\d\d\d\d')
date_pattern4 = re.compile('\d\d\d')

date_patterns_and_formats = [
    (re.compile('\d\d\d\d-(\d)?\d-(\d)?\d'), '%Y-%m-%d'),
    (re.compile('\d\d\d\d/(\d)?\d/(\d)?\d'), '%Y/%m/%d'),
    (re.compile('\d\d\d\d'), '%Y')]

date_patterns_and_formats_for_filenames = [
    (re.compile('\d\d\d\d-(\d)?\d-(\d)?\d'), '%Y-%m-%d'),
    (re.compile('\d\d\d\d/(\d)?\d/(\d)?\d'), '%Y/%m/%d')]


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


def pretty_print(pattern):
    for r in range(pattern.shape[0]):
        for c in range(pattern.shape[1]):
            color = pattern[r, c]
            if color is None:
                sys.stdout.write('. ')
            elif color == WHITE:
                sys.stdout.write('o ')
            elif color == BLACK:
                sys.stdout.write('x ')
            else:
                sys.stdout.write(color + ' ')
        sys.stdout.write('\n')


def get_game_date_from_sgf(sgf_game, pathname=""):
    root = sgf_game.get_root()
    if not root.has_property('DT'):
        sys.stderr.write("Missing DT in filename: %s\n" % pathname)
        return None        
    dt_value = root.get_raw('DT').decode(root.get_encoding())
    return get_game_date_from_text(dt_value, pathname)


def get_game_date_from_text(dt_value, pathname="", verbose=False):
    """
    Retrieves the date when a game was played, given the DT property value
    from a SGF, and optionally a pathname (which is used as a "last resort" in
    case the text date extraction failed, in case the collection containst date
    information in the filename itself.
    """

    if verbose:
        print("DT:[%s]" % dt_value)
    search_result = date_pattern1.search(dt_value)
    if search_result is None:
        if verbose:
            print("Failed to find a datetime in the SGF. Trying in file name")
        # some game collections have the date in the filename
        search_result = date_pattern1.search(pathname)
        if search_result is None:
            if verbose:
                print("Failed to find a datetime. Trying simpler patterns...")
            for p in [date_pattern2, date_pattern3, date_pattern4]:
                search_result = p.search(dt_value)
                if search_result is not None:
                    if verbose:
                        print("Found a match:", search_result.group(0))
                    break
    if search_result is None:
        sys.stderr.write("Failed to find a datetime in the SGF or in filename: %s. DT: [%s]\n" % (pathname, dt_value))
        return None
    search_result = search_result.group(0)
    # This takes care of date such as: 1996-00-00 or 1996-09-00
    search_result = re.sub("-00", "-01", search_result)
    search_result = re.sub("/00", "/01", search_result)
    # TODO how to handle games from years < 1700?
    try:
        return pd.to_datetime(search_result)    
    except ValueError as e:
        sys.stderr.write("Cannot convert value [%s] to datetime. Error: %s\n" %
                         (search_result, e))
        return None


def get_game_date_from_text(dt_value, pathname="", verbose=False):
    """
    Retrieves the date when a game was played, given the DT property value
    from a SGF, and optionally a pathname (which is used as a "last resort" in
    case the text date extraction failed, in case the collection containst date
    information in the filename itself.
    """

    if verbose:
        print("DT:[%s]" % dt_value)

    result_from_dt = extract_date_from_text(dt_value, date_patterns_and_formats)
    if result_from_dt is not None:
        return result_from_dt

    result_from_dt = extract_date_from_text(
        pathname,
        date_patterns_and_formats_for_filenames)
    if result_from_dt is not None:
        return result_from_dt

    return None

def extract_date_from_text(text, date_patterns_and_formats):
    for (date_pattern, date_format) in date_patterns_and_formats:
        search_result = date_pattern.search(text)
        if search_result is not None:
            search_result = search_result.group(0)
            # This takes care of date such as: 1996-00-00 or 1996-09-00
            search_result = re.sub("-00", "-01", search_result)
            search_result = re.sub("/00", "/01", search_result)
            try:
                result = datetime.strptime(search_result, date_format)
                if result.year <= datetime.now().year:
                    return result
                else:
                    sys.stderr.write("Game has year in the future: %s "
                                     "date text: %s" %
                                     (result.year, text))
            except ValueError as e:
                sys.stderr.write("Cannot convert value [%s] to datetime using "
                                 "format: [%s] Error: %s\n" %
                                 (search_result, date_format, e))
                return None
    return None
            
