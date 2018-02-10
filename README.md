The goal is to process a collection of SGF files and identify common patterns.

First version (v0): very simple, working on predefined pattern size.
Processing step for each new game:
- read next move, generate new board position
- for all possible ways in which the new move can be part of a pattern, read that part of the board containing the latest move, effectively resulting in a pattern (of the predefined size)
- normalize the pattern with the new move in it (to take care of symmetries and color inversions)
- attach edges/corners when possible
- if it is not in the index already, add it to the index (with count 1, and info about current SGF/date/place/move/location-on-board)
- else, if it is in the index, increase the count and add same game info as above

Plans for the future (v*): more "unsupervised", with dynamic pattern sizes; for instance, for the same current move, it will look at small 4x4 patterns say enclosing the move, but also at 10x10 quarters of the board, 19x10 halves of the board, etc, as well as whole board, in an attempt to identify both local and global patterns.

Multiple passes through the SGF collection may be necessary to reach the proper balance (between number of patterns and value of information from each pattern: too many patterns may spread out too thin (1 game only for instance), not to mention computational problems; too few patterns and then we don't get much useful info out of it).

Runing unit-tests:

```
python -m unittest discover -s tests
```

Usage:

```
python examples/find_frequent_patterns.py <sgf dir> <pattern height> <pattern width> <min_stones> <max_stones> <max_num_moves> <only_corner_patterns>
```

Example usage:
```
python examples/find_frequent_patterns.py "SOME_DIRECTORY_CONTAINING_ALPHAGO_SGFS" 10 10 10 15 40 True
```

Example output:

```
Number matches: 24
= = = = = = = = = = =
= . . . . . . . . . .
= . . . . o o o . . .
= . . o o x x x . . .
= . . x x . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
Number matches: 24
= = = = = = = = = = =
= . . . . . . . . . .
= . . . . o o o . . .
= . . o o x x x x . .
= . . x x . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
Number matches: 15
= = = = = = = = = = =
= . . . . . . . . . .
= . o x . . . . . . .
= . . o x . . . . . .
= . . o x . . . . . .
= . . o x . . . . . .
= . o x . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
Number matches: 14
= = = = = = = = = = =
= . . . . . . . . . .
= . . . . . . . . . .
= . . o o . x . . . .
= . . x o . . . . . .
= . . x . . . . . . .
= . . x o o . . . . .
= . . . x . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
Number matches: 13
= = = = = = = = = = =
= . . . . . . . . . .
= . o x . . . . . . .
= . . o x . . . . . .
= . . o x . . . . . .
= . . o x . . . . . .
= . o x . . . . . . .
= . x . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
= . . . . . . . . . .
[...]
```
