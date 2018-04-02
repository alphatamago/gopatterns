from collections import namedtuple
import re
import sys
import time

import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

from gopatterns.common import *
from utils.jgoboard_utils import *

if __name__ == '__main__':

    csv_input = sys.argv[1]
    output_dir = sys.argv[2]

    TIMELINE_COL = "version"

    start = time.time()
    (collection_df, versions, pattern_count_by_version,
     pattern_frequency_in_epochs) = index_patterns(
        csv_input, order_by_timeline=False,
        timeline_column=TIMELINE_COL
    )
    print ("Done in time:", time.time()-start)
    
    MIN_EPOCHS_WITH_PATTERN = 1
    MIN_DELTA_COLORS = None
    MAX_DELTA_COLORS = None
    MIN_STONES = 8
    MAX_STONES = 12
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
            max_display_patterns_global=10000,
            max_display_patterns_per_version=None,
            unique_patterns=True,
            min_num_stones=MIN_STONES,
            max_num_stones=MAX_STONES,
            min_delta_colors=MIN_DELTA_COLORS,
            max_delta_colors=MAX_DELTA_COLORS,
            min_epochs_with_pattern=MIN_EPOCHS_WITH_PATTERN,
            xticks=None,
            html_filename="patterns.html",
            imgdir="img")
