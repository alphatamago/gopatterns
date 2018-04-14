"""
Example program that processes the training SGFs from Leela Zero found here:
https://sjeng.org/zero/all.sgf.xz
This is done on a snapshot on the SGFs at the link above from Feb 25, 2018
when the strongest version was a91721af around 8500 on LZ Elo scale.
"""

from collections import namedtuple
import os
import sys

import numpy as np
import pandas as pd

from gopatterns.common import *
from gopatterns.indexer import PatternIndex, BLACK, WHITE
from utils.jgoboard_utils import *
from utils.leelazero_utils import *

from sgfmill import sgf

def main(argv):    
    logging.getLogger().setLevel(logging.DEBUG)

    description = ("Identifying patterns in a collection of SGF files thare "
                   " are all concatenated together in one big file, such as "
                   " the Leela Zero training game records.")
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

    # Skipping the first skip_num_games games
    skip_num_games = 0

    max_num_versions = 1000
    max_games_per_version = 1000
    min_games_per_version = 200

    try:
        pathname = argv[1]
        pattern_dim1 = int(argv[2])
        pattern_dim2 = int(argv[3])
        min_stones_in_pattern = int(argv[4])
        max_stones_in_pattern = int(argv[5])    
        max_moves = int(argv[6])
        only_corners = bool(argv[7])
        output_dir = argv[8]
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
    print("only_corners:", only_corners)
    
    index = PatternIndex(pat_dim=(pattern_dim1, pattern_dim2),
                         min_stones_in_pattern=min_stones_in_pattern,
                         max_stones_in_pattern=max_stones_in_pattern,
                         max_moves=max_moves,
                         only_corners=only_corners)

    VersionPatternInfo = namedtuple('VersionPatternInfo', ['num_games',
                                                           'num_patterns'])

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

    pattern_count_by_version = {}
    pattern_frequency_in_epochs = {}

    stop = False
    for line in open(pathname):
        if stop: break
        if line.startswith(SGF_START):
            # print(len(current_game))
            num_games += 1
            if num_games % 10000 == 0:
                print("#games", num_games, "#versions", len(versions),
                      "len(current_game)", len(current_game))
                if len(versions):
                    print("most recent version:", versions[-1])
            if num_games < skip_num_games:
                current_game = ""
            if current_game:
                if not current_game.startswith(SGF_START):
                    print(current_game)
                    sys.exit(1)
                if num_games >= skip_num_games:
                    versions_in_game = get_versions_from_line(current_game)

                    sgf_bytes = current_game.encode('utf-8')
                    assert len(versions_in_game) <= 2
                    # Reset, start a new game record
                    current_game = ""
                    for version in versions_in_game:
                        version = version[:8]
                        if version not in patterns_in_version:
                            print("New version:", version)
                            print ("Num games and patterns last few version:")
                            for v, vpi in list(patterns_in_version.items())[-5:]:
                                print(v, ":", vpi.num_games, vpi.num_patterns)
                            print("#games", num_games, "#versions", len(versions))
                            if len(patterns_in_version) >= max_num_versions:
                                stop = True
                                print("Reached max_num_versions",
                                      len(patterns_in_version))
                                break
                            versions.append(version)
                            patterns_in_version[version] = VersionPatternInfo(
                                0, 0)
                        if patterns_in_version[version].num_games < max_games_per_version:
                            (patterns_found, _) = index.find_patterns_in_game_str(
                                sgf_bytes, str(num_games))
                            # print('sgf')
                            if not patterns_found:
                                print("No patterns:", sgf_bytes)
                            for p in patterns_found:
                                pattern = np_pattern_to_string(p)
                                if version not in pattern_count_by_version:
                                    pattern_count_by_version[version] = {}
                                if pattern not in pattern_count_by_version[version]:
                                        pattern_count_by_version[version][pattern] = 0
                                pattern_count_by_version[version][pattern] += 1

                                # versions_col.append(version)
                                #p atterns_col.append(np_pattern_to_string(pattern))
                                ver_pat_info = patterns_in_version[version]
                                patterns_in_version[version] = VersionPatternInfo(
                                    ver_pat_info.num_games, ver_pat_info.num_patterns + 1)
                            ver_pat_info = patterns_in_version[version]
                            patterns_in_version[version] = VersionPatternInfo(
                                ver_pat_info.num_games + 1, ver_pat_info.num_patterns)
        current_game += line

    # pattern_frequency_in_epochs[pattern][version] = (count, frequency)
    # (of pattern in epoch)
    pattern_frequency_in_epochs = {}
    for version, pattern_infos in pattern_count_by_version.items():
        num_patterns_in_version = sum([v for v in pattern_infos.values()])
        assert num_patterns_in_version > 0
        for pattern, count in pattern_infos.items():
            if pattern not in pattern_frequency_in_epochs:
                pattern_frequency_in_epochs[pattern] = {}
            assert version not in pattern_frequency_in_epochs[pattern]
            freq = 1.0 * count / num_patterns_in_version
            pattern_frequency_in_epochs[pattern][version] = (count, freq)
        
    sorted_patterns = index.get_frequent_patterns()
    print ("Number patterns found:", len(index.index_), "number of games:",
           num_games)
    print ("Examples:")
    num_show = 25
    print("Most popular", num_show)
    for v in sorted_patterns[:num_show]:
        print ("Number matches:", len(v.matches)) 
        pretty_print (v.pattern)

    logging.info("writing CSV file with patterns")
    patterns_col = []
    versions_col = []
    run_name = output_dir
    for v in versions:
        for p, c in pattern_count_by_version[v].items():
            # TODO optimize by adding count column, DUH...
            for i in range(c):
                versions_col.append(v)
                patterns_col.append(p)
    df = pd.DataFrame(data={'pattern' : patterns_col,
                            'version' : versions_col})
    df.to_csv(path_or_buf = "leelazero_%s_skip_num_games%s_max_num_versions%s_max_games_per_version%s.csv" %
              (run_name, skip_num_games, max_num_versions, max_games_per_version),
              index = False)

    # TODO refactor so we do the rest optionally
    
    assert set(versions) == set(patterns_in_version.keys())
    assert set(versions) == set(pattern_count_by_version.keys())
    
    # Drop versions that are two sparse
    dropped_versions = set()
    for version in patterns_in_version.keys():
        if patterns_in_version[version].num_games < min_games_per_version:
            dropped_versions.add(version)
            del pattern_count_by_version[version]
            logging.info("dropping version %s num_games %s" % (
                version,
                patterns_in_version[version].num_games))

    patterns_without_version = []
    deleted_version_from_patterns_without_version = 0
    for p, vinfo in pattern_frequency_in_epochs.items():
        for v in dropped_versions:
            try:
                del vinfo[v]
                deleted_version_from_patterns_without_version += 1
            except:
                pass
        if len(vinfo) == 0:
            patterns_without_version.append(p)

    logging.info("Num versions deleted from patterns_without_version: %s",
                 deleted_version_from_patterns_without_version)

    logging.info("Num patterns_without_version: %s", len(patterns_without_version))
    
    count_dropped_patterns_displayed = 0
    for p in patterns_without_version:
        del pattern_frequency_in_epochs[p]
        if count_dropped_patterns_displayed < 3:
            logging.info("Dropping pattern with no epochs info:")
            print(p)
            count_dropped_patterns_displayed += 1

    logging.info("Dropped %s patterns without epoch info" % len(patterns_without_version))

    updated_versions = []
    for v in versions:
        if v not in dropped_versions:
            updated_versions.append(v)
        else:
            logging.info("Skipping version: %s", v)

    versions = updated_versions

    logging.info("Epochs to keep: %s", versions)
    
    # Sanity check
    versions_set = set(versions)
    for v in pattern_count_by_version:
        if v not in versions_set:
            logging.info("Unexpected version in pattern_count_by_version %s", v)
            assert(False)
    for p, vinfo in  pattern_frequency_in_epochs.items():
        for v in vinfo.keys():
            if v not in versions_set:
                logging.info("Unexpected version in pattern_frequency_in_epochs %s", v)
                assert(False)

    MIN_EPOCHS_WITH_PATTERN = 1
    MIN_DELTA_COLORS = None
    MAX_DELTA_COLORS = None
    MAX_DISPLAY_PATTERNS = 1000
    suffix = "minepochs.%s_mindelta.%s_maxdelta.%s" % (MIN_EPOCHS_WITH_PATTERN,
                                                       MIN_DELTA_COLORS,
                                                       MAX_DELTA_COLORS)
    generate_patterns_frequency_html(
            versions,
            pattern_count_by_version, 
            pattern_frequency_in_epochs,
            output_dir,
            display_global=True,
            display_by_version=False,
            max_display_patterns_global=MAX_DISPLAY_PATTERNS,
            max_display_patterns_per_version=None,
            unique_patterns=True,
            min_num_stones=min_stones_in_pattern,
            max_num_stones=max_stones_in_pattern,
            min_delta_colors=MIN_DELTA_COLORS,
            max_delta_colors=MAX_DELTA_COLORS,
            min_epochs_with_pattern=MIN_EPOCHS_WITH_PATTERN,
            xticks=None,
            html_filename="patterns.html",
            imgdir="img")

    
if __name__ == '__main__':
    main(sys.argv)
