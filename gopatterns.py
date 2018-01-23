from collections import defaultdict, namedtuple
import fnmatch
import os
import sys

import numpy as np

from sgfmill import sgf, sgf_moves

EDGE = '='
BLACK = 'b'
WHITE = 'w'

# Temporary chars used for swapping colors
# Must be different than BLACK and WHILTE!
WHITE_REPL = 'W'
BLACK_REPL = 'B'

PatternMatchInfo = namedtuple('PatternMatchInfo',
                              ['filename', 'move_num', 'location'])

PatternIndexValue = namedtuple('PatternIndexValue',
                               ['pattern', 'matches'])
"""
PatternIndexValue is the value in the pattern index

pattern: the actual pattern
matches: map of filename-to-PatternMatchInfo instances for where the pattern
was found
"""

PatternMatchFeatures = namedtuple('PatternMatchFeatures',
                                  ['pattern',
                                   'info',
                                   'edge_up', 'edge_down',
                                   'edge_left', 'edge_right'])
"""
edge_*: boolean fields which tell us if the pattern is touching a given edge
pattern: numpy array represntation of the pattern
info: a PatternMatchInfo instance
"""

class PatternIndex(object):
    """
    Index for patterns in a collection of Go game records.
    """

    def __init__(self, pat_dim,
                 min_stones_in_pattern, max_stones_in_pattern,
                 max_moves):
        self.pat_dim = pat_dim

        # Only index patterns if they have at least this number of stones
        self.min_stones_in_pattern_ = min_stones_in_pattern

        # Only index patterns if they have at most this number of stones
        self.max_stones_in_pattern_ = max_stones_in_pattern
        
        # Do not try to find patterns beyone this number of moves in each game,
        # if defined.
        self.max_moves_ = max_moves

        # self.index[pattern_hash(pattern)] = 
        self.index_ = {}


    def pattern_transformations(self, pattern):
        result = [pattern]
        result.append(np.rot90(result[-1]))
        result.append(np.rot90(result[-1]))
        result.append(np.rot90(result[-1]))
        result.append(np.fliplr(result[-1]))
        result.append(np.rot90(result[-1]))
        result.append(np.rot90(result[-1]))
        result.append(np.rot90(result[-1]))
        return result


    def pattern_hash(self, original_pattern):
        """
        Computes a hash out of a pattern to be able to index it, since we
        cannot index a matrix.
        Normalize pattern for rotations, flips, etc, as well as for color
        swapping.

        pattern: a numpy array

        returns: (normalized_pattern_hash, normalized_pattern)
        """

        transforms = self.pattern_transformations(original_pattern)
        
        # swap colors
        pattern = original_pattern.copy()
        pattern[pattern == WHITE] = WHITE_REPL
        pattern[pattern == BLACK] = BLACK_REPL
        pattern[[pattern == WHITE_REPL]] = BLACK
        pattern[[pattern == BLACK_REPL]] = WHITE
        transforms += self.pattern_transformations(pattern)
        assert len(transforms) == 16
        hashed_transforms = sorted([(p.tostring(), p) for p in transforms],
                                   key=lambda x: x[0])
        return hashed_transforms[0]


    def add_to_index(self, pattern, info):
        """
        pattern: the actual board pattern to add
        info: a PatternMatchInfo instance
        """
        pat_hash, norm_pat = self.pattern_hash(pattern)
        try:
            value = self.index_[pat_hash]
        except KeyError:
            value = PatternIndexValue(pattern=norm_pat,
                                      matches=defaultdict(list))
            self.index_[pat_hash] = value
        value.matches[info.filename].append(info)


    def extract_board_patterns_after_move(self, pathname, num_moves,
                                          board, row, col):
        """
        Given a board (numpy array) and a pattern size pat_dim, extract the
        pattern assumming that (row, col) board coordinates are in (x, y) pattern
        coordinates.
        If the pattern won't fully fit on the board this way, move on.
        """
        
        # Consider all possible ways in which the current (row, col)
        # location can be in a pattern of dimensions pat_dim, and filter out
        # some that may be redundant or undesirable, for instance if we can
        # match by touching a corner, we don't match other variations that don't
        # touch a corner

        # Contains PatternMatchFeatures instances.
        possible_matches = []

        # Keep track of whether we have a corner match; if so, we can use this
        # info to avoid non-corner matches
        has_corner = False
        
        np_board = np.array(board.board)
        for x in range(self.pat_dim[0]):
            for y in range(self.pat_dim[1]):
                # We regard (row, col) as being at location (x, y) in the
                # pat_dim pattern, if possible

                if ((row - x < 0) or
                    (row + self.pat_dim[0] - x > np_board.shape[0]) or
                    (col - y < 0) or
                    (col + self.pat_dim[1] - y > np_board.shape[1])):
                    # This particular way of trying to fit a pat_dim pattern
                    # containing the current move will not work, the pattern is
                    # not completely inside the board.
                    continue

                pat = np_board[row - x : row - x + self.pat_dim[0],
                             col - y : col - y + self.pat_dim[1]]

                num_stones = np.count_nonzero((pat == BLACK) | (pat == WHITE))
                if (num_stones < self.min_stones_in_pattern_ or
                    num_stones > self.max_stones_in_pattern_):
                    # Failed the number-of-stones test
                    continue
                
                if self.check_adjacent_stones_outside_pattern(np_board, x, y,
                                                              row, col):
                    # There are stones outside of the pattern, in contact with
                    # stones inside, this will not be a good pattern.
                    continue

                # Check side/corner anchoring
                num_edges = 0
                edge_up = edge_down = edge_left = edge_right = False
                if row - x == 0:
                    num_edges += 1
                    edge_up = True
                if row + self.pat_dim[0] - x == np_board.shape[0]:
                    num_edges += 1
                    edge_down = True
                if col - y == 0:
                    num_edges += 1
                    edge_left = True
                if col + self.pat_dim[1] - y == np_board.shape[1]:
                    num_edges += 1
                    edge_right = True

                if ((edge_up and edge_right) or
                    (edge_right and edge_down) or
                    (edge_down and edge_left) or
                    (edge_left and edge_up)):
                    has_corner = True

                # Attach all adjacent edges
                if edge_up:
                    pat = np.vstack((np.array([EDGE] * pat.shape[1]), pat))
                if edge_down:
                    pat = np.vstack((pat, np.array([EDGE] * pat.shape[1])))
                if edge_left:
                    pat = np.hstack(
                        (np.array([EDGE] * pat.shape[0]).reshape(
                            (pat.shape[0], 1)),
                         pat))
                if edge_right:
                    pat = np.hstack(
                        (pat,
                         np.array([EDGE] * pat.shape[0]).reshape(
                             (pat.shape[0], 1))))

                pattern_match_info = PatternMatchInfo(filename=pathname,
                                                      move_num=num_moves,
                                                      location=(row-x, col-y))
                possible_matches.append(
                    PatternMatchFeatures(pattern=pat,
                                         edge_up=edge_up,
                                         edge_down=edge_down,
                                         edge_left=edge_left,
                                         edge_right=edge_right,
                                         info=pattern_match_info))

        for pattern_features in possible_matches:
            # Since one of the pattern_features has_corner, skip the ones
            # without corner match
            if has_corner:
                if not((pattern_features.edge_up and
                        pattern_features.edge_right) or
                    (pattern_features.edge_right and
                     pattern_features.edge_down) or
                    (pattern_features.edge_down and
                     pattern_features.edge_left) or
                    (pattern_features.edge_left and
                     pattern_features.edge_up)):
                    continue
            self.add_to_index(
                pattern_features.pattern,
                pattern_features.info)


    def check_adjacent_stones_outside_pattern(self, board, x, y, row, col):
        """
        Check if there are any stones outside the pattern boundaries, which
        are in direct contact with stones inside the pattern.
        
        board: a numpy array representation of the board
        x: pattern row
        y: pattern column
        row: board row
        col: board column
        return: True if there are adjacent stones outside pattern, else False
        """

        # Check first pattern column, if not on left-edge
        if col - y > 0:
            c = col - y
            for r in range(row - x, row - x + self.pat_dim[0]):
                if (board[r, c] is not None) and (board[r, c - 1] is not None):
                    # Found outside adjacent, not a good pattern
                    return True
        # Check last pattern column, if not on right-edge
        if (col - y + self.pat_dim[1]) < board.shape[1] - 1:
            c = col - y + self.pat_dim[1]
            for r in range(row - x, row - x + self.pat_dim[0]):
                if (board[r, c] is not None) and (board[r, c + 1] is not None):
                    # Found outside adjacent, not a good pattern
                    return True
        # Check first pattern row, if not on top-edge
        if row - x > 0:
            r = row - x
            for c in range(col - y, col - y + self.pat_dim[1]):
                if (board[r, c] is not None) and (board[r - 1, c] is not None):
                    # Found outside adjacent, not a good pattern
                    return True
        # Check last pattern row, if not on bottom-edge
        if row - x + self.pat_dim[0] < board.shape[0] - 1:
            r = row - x + self.pat_dim[0]
            for c in range(col - y, col - y + self.pat_dim[1]):
                if (board[r, c] is not None) and (board[r + 1, c] is not None):
                    # Found outside adjacent, not a good pattern
                    return True
        return False
        

    def find_patterns_in_game(self, pathname):
        """
        pathname: path to SGF file
        """

        f = open(pathname, "rb")
        sgf_src = f.read()
        f.close()
        try:
            sgf_game = sgf.Sgf_game.from_bytes(sgf_src)
            board, plays = sgf_moves.get_setup_and_moves(sgf_game)
        except Exception as e:
            print("Warning: cannot process game", pathname, ", reason:", e)
            return

        num_moves = 0
        num_found = 0
        for colour, move in plays:
            if self.max_moves_ is not None and num_moves > self.max_moves_:
                break
            if move is None:
                continue
            row, col = move
            num_moves += 1
            try:
                board.play(row, col, colour)
                self.extract_board_patterns_after_move(pathname,
                                                       num_moves,
                                                       board,
                                                       row, col)
            except ValueError as e:
                print("Error processing", pathname, "at move:", num_moves, ":",
                      e)
                return


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

    try:
        pathname = argv[1]
        pattern_dim1 = int(argv[2])
        pattern_dim2 = int(argv[3])
        min_stones_in_pattern = int(argv[4])
        max_stones_in_pattern = int(argv[5])    
        max_moves = int(argv[6])
    except:
        print(description)
        print(usage)
        sys.exit(1)
        
    print("pathname:", pathname)
    print("pattern size:", pattern_dim1, "x", pattern_dim2)
    print("min_stones_in_pattern:", min_stones_in_pattern)
    print("max_stones_in_pattern", max_stones_in_pattern)
    print("max_moves per game:", max_moves)
    
    index = PatternIndex(pat_dim=(pattern_dim1, pattern_dim2),
                         min_stones_in_pattern=min_stones_in_pattern,
                         max_stones_in_pattern=max_stones_in_pattern,
                         max_moves=max_moves)
           
    num_games = 0
    matches = []
    for root, dirnames, filenames in os.walk(pathname):
        for filename in fnmatch.filter(filenames, '*.sgf'):
            path = os.path.join(root, filename)
            if num_games < 3:
                print("Processing", path)
            index.find_patterns_in_game(path)
            num_games += 1

    print ("Number patterns found:", len(index.index_), "number of games:",
           num_games)
    print ("Examples:")
    sorted_patterns = sorted(
        index.index_.items(),
        key=lambda x:len(x[1].matches),
        reverse=True)

    num_show = 25
    print("Most popular:")
    for _, v in sorted_patterns[:num_show]:
        print ("Number matches:", len(v.matches)) 
        pretty_print (v.pattern)

    if len(index.index_) > num_show:
        print()
        print("... skipping", len(index.index_) - num_show, "patterns")


if __name__ == '__main__':
    main(sys.argv)
