"""
Example program that processes the training SGFs from Leela Zero found here:
https://sjeng.org/zero/all.sgf.xz
This is done on a snapshot on the SGFs at the link above from Feb 25, 2018
when the strongest version was a91721af around 8500 on LZ Elo scale.
"""

from collections import namedtuple
import fnmatch
import os
import sys

import numpy as np
import pandas as pd

from gopatterns.common import *
from gopatterns.indexer import PatternIndex, BLACK, WHITE
from utils.leelazero_utils import *

from sgfmill import sgf

def main(argv):    
    description = ("Identifying patterns in a collection of SGF files thare are "
                  "all concatenated together in one big file, such as the Leela "
                  "Zero training game records.")
    usage = ("%s <filename> <pattern height>"
             " <pattern width> <min_stones> <max_stones>"
             " <max_num_moves> <only_corner_patterns?") % argv[0]

    pathname = ""
    pattern_dim1 = 0
    pattern_dim2 = 0
    min_stones_in_pattern = 0
    max_stones_in_pattern = 0
    max_moves = 0
    only_corners = False

    first_index = 0
    max_num_versions = 100
    max_games_per_version = 1000

    try:
        pathname = argv[1]
        pattern_dim1 = int(argv[2])
        pattern_dim2 = int(argv[3])
        min_stones_in_pattern = int(argv[4])
        max_stones_in_pattern = int(argv[5])    
        max_moves = int(argv[6])
        only_corners = bool(argv[7])
        run_name = argv[8]
    except:
        print(description)
        print(usage)
        sys.exit(1)

    assert run_name
        
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
    print("only_corners:", only_corners)
    print("run_name:", run_name)
    
    index = PatternIndex(pat_dim=(pattern_dim1, pattern_dim2),
                         min_stones_in_pattern=min_stones_in_pattern,
                         max_stones_in_pattern=max_stones_in_pattern,
                         max_moves=max_moves,
                         only_corners=only_corners)

    VersionPatternInfo = namedtuple('VersionPatternInfo', ['num_games',
                                                           'patterns'])

    SGF_START = "(;GM"
    
    num_games = 0
    # Since all the game records are in the same physical file, we need to keep
    # track of the string for the current SGF.
    # We identify each new SGF as starting on a new line, with: '(;GM' followed
    # by more characters, more lines.
    current_game = ""
    patterns_in_version = {}
    # Training versions, in the order in chronological order
    versions = []

    for root, dirnames, filenames in os.walk(pathname):
        for f in fnmatch.filter(filenames, '*.sgf'):
            filename = os.path.join(root, f)

            num_games += 1
            if num_games % 1000 == 0:
                print("#games", num_games, "#versions", len(versions))
                if len(versions):
                    print("most recent version:", versions[-1])
            if num_games >= first_index:
                parent_directory = os.path.split(os.path.split(os.path.split(filename)[0])[0])[-1]
                versions_in_game = [parent_directory]
                assert len(versions_in_game) <=  2
                # Reset, start a new game record
                current_game = ""
                for version in versions_in_game:
                    if version not in patterns_in_version:
                        print ("Num games and patterns per version:")
                        for v, vpi in patterns_in_version.items():
                            print(v, ":", vpi.num_games, len(vpi.patterns))
                        print("New version:", version)
                        if len(patterns_in_version) >= max_num_versions:
                            print("Reached max_num_versions",
                                  len(patterns_in_version))
                            break
                        versions.append(version)
                        patterns_in_version[version] = VersionPatternInfo(
                            0, [])
                    ver_pat_info = patterns_in_version[version]
                    if ver_pat_info.num_games < max_games_per_version:
                        (patterns_found, _) = index.find_patterns_in_game(filename)
                        # print('sgf')
                        if not patterns_found:
                            print("No patterns:", filename)
                        for pattern in patterns_found:
                            ver_pat_info.patterns.append(pattern)
                        patterns_in_version[version] = VersionPatternInfo(
                            ver_pat_info.num_games + 1,
                            ver_pat_info.patterns)

    sorted_patterns = index.get_frequent_patterns()
    print ("Number patterns found:", len(index.index_), "number of games:",
           num_games, "number of epochs:", len(versions))
    print ("Examples:")
    num_show = 25
    print("Most popular", num_show)
    for v in sorted_patterns[:num_show]:
        print ("Number matches:", len(v.matches)) 
        pretty_print (v.pattern)

        
    patterns_col = []
    versions_col = []
    for v, vpi in patterns_in_version.items():
        for p in vpi.patterns:
            versions_col.append(v)
            patterns_col.append(np_pattern_to_string(p))
    df = pd.DataFrame(data={'pattern' : patterns_col,
                            'version' : versions_col})
    df.to_csv(path_or_buf = "leelazero_%s_first_index%s_max_num_versions%s_max_games_per_version%s.csv" %
              (run_name, first_index, max_num_versions, max_games_per_version),
              index = False)

if __name__ == '__main__':
    main(sys.argv)
