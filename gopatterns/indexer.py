"""
The indexer is the core of GoPatterns.
"""

from collections import defaultdict, namedtuple

import numpy as np

from sgfmill import sgf, sgf_moves

from gopatterns.common import *

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
                 max_moves,
                 only_corners):
        self.pat_dim = pat_dim

        # Only index patterns if they have at least this number of stones
        self.min_stones_in_pattern_ = min_stones_in_pattern

        # Only index patterns if they have at most this number of stones
        self.max_stones_in_pattern_ = max_stones_in_pattern
        
        # Do not try to find patterns beyone this number of moves in each game,
        # if defined.
        self.max_moves_ = max_moves

        # If true, ignore any pattern that does not include a corner
        self.only_corners = only_corners

        # self.index[pattern_hash(pattern)] = 
        self.index_ = {}


    def find_patterns_in_game(self, pathname):
        """
        Public method that takes a path to a SGF file, reads the file, finds
        patterns, adds them to the index and also returns them to the caller.

        One can call this repeatedly to iterate through a game collection and
        then consult the index to find the most frequent patterns for instance.

        pathname: path to SGF file
        
        return: pair containing (patterns, date) where patterns is a list of
        each found pattern (normalized) as a numpy array
        """
        
        f = open(pathname, "rb")
        sgf_src = f.read()
        f.close()

        sgf_game = None
        try:
            sgf_game = sgf.Sgf_game.from_bytes(sgf_src)
            board, plays = sgf_moves.get_setup_and_moves(sgf_game)
        except Exception as e:
            print("Warning: cannot process game", pathname, ", reason:", e)
            return ([], None)

        patterns_found = []
        num_moves = 0
        num_found = 0
        date = None
        try:
            date = get_game_date_from_sgf(sgf_game, pathname)
        except:
            # TODO - log this, or add some counter
            pass
        for colour, move in plays:
            if self.max_moves_ is not None and num_moves > self.max_moves_:
                break
            if move is None:
                continue
            row, col = move
            num_moves += 1
            try:
                board.play(row, col, colour)
                for pattern in self.extract_board_patterns_after_move_(pathname,
                                                                       num_moves,
                                                                       board,
                                                                       row, col):
                    patterns_found.append(pattern)
            except ValueError as e:
                print("Error processing", pathname, "at move:", num_moves, ":",
                      e)
                break
        return (patterns_found, date)


    def num_patterns(self):
        return len(self.index_)


    def get_frequent_patterns(self):
        """
        Return the indexed patterns, most frequent first.
        """
        return [x[1] for x in sorted(
            self.index_.items(),
            key=lambda x:len(x[1].matches),
            reverse=True)]


    def pattern_transformations_(self, pattern):
        """
        Private method.
        Returns all the symmetries of the given pattern.
        Color swapping is handled separately.
        """
        result = [pattern]
        result.append(np.rot90(result[-1]))
        result.append(np.rot90(result[-1]))
        result.append(np.rot90(result[-1]))
        result.append(np.fliplr(result[-1]))
        result.append(np.rot90(result[-1]))
        result.append(np.rot90(result[-1]))
        result.append(np.rot90(result[-1]))
        return result


    def pattern_hash_(self, original_pattern):
        """
        Private method.
        Computes a hash out of a pattern to be able to index it, since we
        cannot index a matrix.
        Normalize pattern for rotations, flips, etc, as well as for color
        swapping.

        original_pattern: a numpy array

        returns: (normalized_pattern_hash, normalized_pattern) where
        normalized_pattern_hash is a string representation (hash) of the
        pattern, which normalized_pattern is a numpy array of an equivalent,
        cannonical pattern that is identical to the original_pattern modulo
        symmetries and/or color swaps.
        """

        transforms = self.pattern_transformations_(original_pattern)
        
        # swap colors
        pattern = original_pattern.copy()
        pattern[pattern == WHITE] = WHITE_REPL
        pattern[pattern == BLACK] = BLACK_REPL
        pattern[[pattern == WHITE_REPL]] = BLACK
        pattern[[pattern == BLACK_REPL]] = WHITE
        transforms += self.pattern_transformations_(pattern)
        assert len(transforms) == 16
        hashed_transforms = sorted([(p.tostring(), p) for p in transforms],
                                   key=lambda x: x[0])
        return hashed_transforms[0]


    def add_to_index_(self, pattern, info):
        """
        Private method.
        Adds a pattern to the index.
        Returns the normalized pattern.

        pattern: the actual board pattern to add
        info: a PatternMatchInfo instance
        return: the normalized version of the input pattern (numpy array)
        """
        pat_hash, norm_pat = self.pattern_hash_(pattern)
        try:
            value = self.index_[pat_hash]
        except KeyError:
            value = PatternIndexValue(pattern=norm_pat,
                                      matches=defaultdict(list))
            self.index_[pat_hash] = value
        value.matches[info.filename].append(info)
        return norm_pat


    def extract_board_patterns_after_move_(self, pathname, num_moves,
                                           board, row, col):
        """
        Private method.
        Given a board (numpy array) and a pattern size pat_dim, extract the
        pattern assumming that (row, col) board coordinates are in (x, y) pattern
        coordinates.
        If the pattern won't fully fit on the board this way, move on.

        return: yields each pattern found as a numpy array
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
        already_found_corner_match = False
        
        np_board = board_to_np(board.board)
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
                
                if self.check_adjacent_stones_outside_pattern_(np_board, x, y,
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
                    already_found_corner_match = True

                # Attach all adjacent edges
                if edge_up:
                    pat = np.vstack(( board_to_np([EDGE] * pat.shape[1]),
                                      pat))
                if edge_down:
                    pat = np.vstack((pat,
                                     board_to_np([EDGE] * pat.shape[1])))
                if edge_left:
                    pat = np.hstack(
                        (board_to_np([EDGE] * pat.shape[0]).reshape(
                            (pat.shape[0], 1)),
                         pat))
                if edge_right:
                    pat = np.hstack(
                        (pat,
                         board_to_np([EDGE] * pat.shape[0]).reshape(
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
            # Since one we already_found_corner_match, skip
            # the ones without corner match
            has_corner = ((pattern_features.edge_up and
                           pattern_features.edge_right) or
                          (pattern_features.edge_right and
                           pattern_features.edge_down) or
                          (pattern_features.edge_down and
                           pattern_features.edge_left) or
                          (pattern_features.edge_left and
                           pattern_features.edge_up))
            if self.only_corners and not has_corner:
                continue
            if already_found_corner_match:
                if not has_corner:
                    continue
            normalized_pattern = self.add_to_index_(
                pattern_features.pattern,
                pattern_features.info)
            yield normalized_pattern


    def check_adjacent_stones_outside_pattern_(self, board, x, y, row, col):
        """
        Private method.
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
                if (board[r, c] != EMPTY) and (board[r, c - 1] != EMPTY):
                    # Found outside adjacent, not a good pattern
                    return True
        # Check last pattern column, if not on right-edge
        if (col - y + self.pat_dim[1]) < board.shape[1] - 1:
            c = col - y + self.pat_dim[1]
            for r in range(row - x, row - x + self.pat_dim[0]):
                if (board[r, c] != EMPTY) and (board[r, c + 1] != EMPTY):
                    # Found outside adjacent, not a good pattern
                    return True
        # Check first pattern row, if not on top-edge
        if row - x > 0:
            r = row - x
            for c in range(col - y, col - y + self.pat_dim[1]):
                if (board[r, c] != EMPTY) and (board[r - 1, c] != EMPTY):
                    # Found outside adjacent, not a good pattern
                    return True
        # Check last pattern row, if not on bottom-edge
        if row - x + self.pat_dim[0] < board.shape[0] - 1:
            r = row - x + self.pat_dim[0]
            for c in range(col - y, col - y + self.pat_dim[1]):
                if (board[r, c] != EMPTY) and (board[r + 1, c] != EMPTY):
                    # Found outside adjacent, not a good pattern
                    return True
        return False
