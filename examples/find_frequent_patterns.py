"""
Example program that uses PatternIndex to find most often occurring patterns
in a SGS collection.
"""

import fnmatch
import os
import sys

import numpy as np
import pandas as pd

from gopatterns.common import *
from gopatterns.indexer import PatternIndex, BLACK, WHITE

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


def main(argv):
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

    try:
        pathname = argv[1]
        pattern_dim1 = int(argv[2])
        pattern_dim2 = int(argv[3])
        min_stones_in_pattern = int(argv[4])
        max_stones_in_pattern = int(argv[5])    
        max_moves = int(argv[6])
        only_corners = bool(argv[7])
    except:
        print(description)
        print(usage)
        sys.exit(1)

    output_fname = None
    if len(argv) == 9:
        output_fname = argv[8] + ".txt"
        if os.path.isfile(output_fname):
            print("File already exisits, specify a new name:", output_fname)
            sys.exit(1)
        pd_output_fname = argv[8]

            
    print("pathname:", pathname)
    print("pattern size:", pattern_dim1, "x", pattern_dim2)
    print("min_stones_in_pattern:", min_stones_in_pattern)
    print("max_stones_in_pattern", max_stones_in_pattern)
    print("max_moves per game:", max_moves)
    print("only_corner:", only_corners)
    
    index = PatternIndex(pat_dim=(pattern_dim1, pattern_dim2),
                         min_stones_in_pattern=min_stones_in_pattern,
                         max_stones_in_pattern=max_stones_in_pattern,
                         max_moves=max_moves,
                         only_corners=only_corners)
           
    num_games = 0
    matches = []
    for root, dirnames, filenames in os.walk(pathname):
        for filename in fnmatch.filter(filenames, '*.sgf'):
            path = os.path.join(root, filename)
            print("Processing", path)
            index.find_patterns_in_game(path)
            num_games += 1

    sorted_patterns = index.get_frequent_patterns()

    print ("Number patterns found:", len(index.index_), "number of games:",
           num_games)
    print ("Examples:")

    num_show = 25
    print("Most popular", num_show)
    for v in sorted_patterns[:num_show]:
        print ("Number matches:", len(v.matches)) 
        pretty_print (v.pattern)

    if index.num_patterns() > num_show:
        print()
        print("... skipping", index.num_patterns() - num_show, "patterns")

    if output_fname is not None:
        sys.stdout = open(output_fname, "w")
        print ("#patterns :", len(index.index_), "#games :", num_games)

        matches = []
        patterns = []
        num_matches = []
        for v in sorted_patterns:
            matches.append(','.join(v.matches))
            num_matches.append(len(v.matches))
            patterns.append(np_pattern_to_string(v.pattern))
            print ("#matches :", len(v.matches)) 
            pretty_print (v.pattern)
            print()

        df = pd.DataFrame(data={'pattern' : patterns,
                                # 'matched_sgf': matches}
                                'frequency' : num_matches})
        df.to_csv(path_or_buf = "collection_%s_numgames_%s_numpatterns_%s.csv" %
                  (pd_output_fname, num_games, len(sorted_patterns)),
                   index = False)

if __name__ == '__main__':
    main(sys.argv)
