"""
Example program that finds the patterns of given size in a SGS collection, and
outputs a CSV with the following columns:

pattern sgf_filename year
"""

import fnmatch
import os
import sys

import numpy as np
import pandas as pd

from gopatterns.common import *
from gopatterns.indexer import PatternIndex, BLACK, WHITE


def main(argv):
    logging.getLogger().setLevel(logging.DEBUG)

    description = "Identifying patterns in a collection of SGF files."
    usage = ("%s <sgf dir> <pattern height>"
             " <pattern width> <min_stones> <max_stones>"
             " <max_num_moves>") % argv[0]

    pathname = ""
    pattern_dim1 = 0
    pattern_dim2 = 0
    min_stones_in_pattern = 0
    max_stones_in_pattern = 0
    max_moves = 0
    only_corners = False
    pd_output_fname = None

    try:
        pathname = argv[1]
        pattern_dim1 = int(argv[2])
        pattern_dim2 = int(argv[3])
        min_stones_in_pattern = int(argv[4])
        max_stones_in_pattern = int(argv[5])    
        max_moves = int(argv[6])
        only_corners = bool(argv[7])
        pd_output_fname = argv[8]
    except:
        logging.info(description)
        logging.info(usage)
        sys.exit(1)

            
    logging.info("pathname: %s", pathname)
    logging.info("pattern size: %sx%s", pattern_dim1, pattern_dim2)
    logging.info("min_stones_in_pattern: %s", min_stones_in_pattern)
    logging.info("max_stones_in_pattern %s", max_stones_in_pattern)
    logging.info("max_moves per game: %s", max_moves)
    logging.info("only_corner: %s", only_corners)
    logging.info("pd_output_fname: %s", pd_output_fname)
    
    index = PatternIndex(pat_dim=(pattern_dim1, pattern_dim2),
                         min_stones_in_pattern=min_stones_in_pattern,
                         max_stones_in_pattern=max_stones_in_pattern,
                         max_moves=max_moves,
                         only_corners=only_corners)
           
    patterns = []
    sgf_filenames = []
    years = []
    num_games = 0
    for root, dirnames, filenames in os.walk(pathname):
        # if num_games >= 100: break
        for filename in fnmatch.filter(filenames, '*.sgf'):
            path = os.path.join(root, filename)
            logging.info("Processing %s", path)
            (patterns_found, date) = index.find_patterns_in_game(path)
            if date is not None:
                num_games += 1
                for pattern in patterns_found:
                    patterns.append(np_pattern_to_string(pattern))
                    years.append(date.year)
                    sgf_filenames.append(path)

    df = pd.DataFrame(data={'pattern' : patterns,
                            'sgf_filename' : sgf_filenames,
                            'year' : years})
    df.to_csv(path_or_buf = "collection_%s_numgames_%s.csv" %
              (pd_output_fname, num_games),
              index = False)

if __name__ == '__main__':
    main(sys.argv)
