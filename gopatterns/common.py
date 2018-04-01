from datetime import datetime
import os
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


def print_pat(pattern):
    """
    Prints a string pattern
    """
    # Patterns already have \n as line separators, how convenient...
    print(pattern)


def count_stones(pattern):
    return pattern.count('w') + pattern.count('b')


def count_stones_by_color(pattern, color):
    return pattern.count(color)


def pretty_print(pattern):
    """
    Prints a numpy pattern
    """
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
        # sys.stderr.write("Missing DT in filename: %s\n" % pathname)
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


def build_pattern_timeline(pattern, pattern_frequency_in_epochs, versions):
    result = []
    for v in versions:
        try:
            freq = pattern_frequency_in_epochs[v]
        except KeyError:
            freq = 0.0
        result.append(freq)
    return result


def index_patterns(csv_pathname, timeline_column, order_by_timeline=False):
    # We are reading here a dataset in CSV format, with columns 'pattern' and <timeline_columns>
    # This can be produced for instance like this:
    # find_patterns_in_collection.py <PATH_TO_DIRECOTRY_WITH_SGF_FILES> 9 9 3 10 40 True <some_name>
    collection_df = pd.read_csv(csv_pathname)
    if order_by_timeline:
        collection_df = collection_df.sort_values(by=timeline_column)

    # How many patterns in each epoch
    val_cnt = collection_df[timeline_column].value_counts()
    mean_count = val_cnt.describe()['50%']
    low_freq_epochs = [v for v in val_cnt.index if val_cnt[v]<=.25 * mean_count]
    print("Dropping epochs with low data:", low_freq_epochs)
    collection_df = collection_df.drop(
        collection_df[collection_df[timeline_column].isin(low_freq_epochs)].index)
    versions = collection_df[timeline_column].unique()

    # pattern_count_by_version[version][pattern] = count (of pattern in version)
    pattern_count_by_version = {}
    count = 0
    for index, data in collection_df.iterrows():
        count += 1
        if count % 100000 == 0:
            print("rows: ", count, "out of:", collection_df.shape[0])
        version = data[timeline_column]
        pattern = data['pattern']
        if version not in pattern_count_by_version:
            pattern_count_by_version[version] = {}
        if pattern not in pattern_count_by_version[version]:
            pattern_count_by_version[version][pattern] = 0
        pattern_count_by_version[version][pattern] += 1

    # pattern_frequency_in_epochs[pattern][version] = frequency (of patter in epoch)
    pattern_frequency_in_epochs = {}
    for version, pattern_infos in pattern_count_by_version.items():
        num_patterns_in_version = sum([v for v in pattern_infos.values()])
        assert num_patterns_in_version > 0
        for pattern, count in pattern_infos.items():
            if pattern not in pattern_frequency_in_epochs:
                pattern_frequency_in_epochs[pattern] = {}
            assert version not in pattern_frequency_in_epochs[pattern]
            pattern_frequency_in_epochs[pattern][version] = 1.0 * count / num_patterns_in_version

    return collection_df, versions, pattern_count_by_version, pattern_frequency_in_epochs


def is_pattern_acceptable(pattern, min_delta_colors, max_delta_colors, min_num_stones, max_num_stones):
        num_black_stones = count_stones_by_color(pattern, 'b')
        num_white_stones = count_stones_by_color(pattern, 'w')
        num_stones = num_black_stones + num_white_stones
        if num_stones < min_num_stones or num_stones > max_num_stones:
            # This pattern has too few or too many stones
            return False
        delta = abs(num_black_stones - num_white_stones)
        if ((max_delta_colors is not None and (delta > max_delta_colors)) or
            (min_delta_colors is not None and (delta < min_delta_colors))):
            # This pattern has too large of an imbalance between black/white
            # stones
            return False
        return True
