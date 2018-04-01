import os

import matplotlib
import matplotlib.pyplot as plt

from gopatterns.common import *

def custom_figsize():
    plt.figure(figsize=(8,5))    

def process_pattern_for_jgoboard(pattern, verbose=False):
    """
    Given a pattern as a string, generates info needed to be able to view
    that pattern using jgoboard JS library
    """
    if verbose:
        print(pattern)
    pattern = pattern.replace(' ', '').replace('\r', '')

    board_height = 19
    board_width = 19
    upper_row = -1
    lower_row = -1
    left_col = -1
    right_col = -1
    
    if pattern[0] == ('\n'):
        pattern = pattern[1:]
    if pattern[-1] == ('\n'):
        pattern = pattern[:-1]

    pattern_rows = pattern.split("\n")
  
    
    height = len(pattern_rows)
    width = len(pattern_rows[0])
    if verbose:
        print ("raw dims:", height, width)

    assert len(pattern_rows[0]) == len(pattern_rows[-1])
    
    top_edge = bottom_edge = right_edge = left_edge = False
    if (pattern_rows[0][0] == '=' and pattern_rows[0][-1] == '=' and
        pattern_rows[0][int(len(pattern_rows[0])/2)] == '='):
        top_edge = True
        upper_row = board_height - 1
        height -= 1
    if (pattern_rows[-1][0] == '=' and pattern_rows[-1][-1] == '=' and
        pattern_rows[-1][int(len(pattern_rows[-1])/2)] == '='):
        bottom_edge = True
        lower_row = 0
        height -= 1
    if (pattern_rows[0][0] == '=' and pattern_rows[-1][0] == '=' and
        pattern_rows[int(len(pattern_rows)/2)][0] == '='):
        left_edge = True
        left_col = 0
        width -= 1
    if (pattern_rows[0][-1] == '=' and pattern_rows[-1][-1] == '=' and
        pattern_rows[int(len(pattern_rows)/2)][-1] == '='):
        right_edge = True
        right_col = board_width - 1
        width -= 1

    if top_edge and bottom_edge:
        height = len(pattern_rows) - 2
        board_height = height
        upper_row = board_height - 1
        
    if left_edge and right_edge:
        width = len(pattern_rows[0]) - 2
        board_width = width
        right_col = board_width - 1

    if verbose:
        print ("BH, BW:", board_height, board_width)
        print ("H, W:", height, width)
        print("LC, LR, RC, RR:", left_col, upper_row, right_col, lower_row)
    
    if upper_row == -1:
        if lower_row == -1:
            # not well defined - center it
            upper_row = int(board_height/2) + int(height/2)
        else:
            upper_row = lower_row + height - 1
    lower_row = upper_row - height + 1
    
    if verbose:
        print(left_col, upper_row, right_col, lower_row)
    
    if left_col == -1:
        if right_col == -1:
            # not well defined - center it
            left_col = int(board_width/2) + int(width/2)
        else:
            left_col = right_col - width + 1
    right_col = left_col + width - 1
            
    if verbose:
        print(left_col, upper_row, right_col, lower_row)
        
    assert left_col >= 0 and left_col < board_width
    assert right_col >= 0 and right_col < board_width
    left_col = chr(ord('A') + left_col)
    if ord(left_col) >= ord('I'):
        old_left_col = left_col
        left_col = chr(ord(left_col) + 1)
        if verbose:
            print('right col was shifted from', old_left_col, 'to:', left_col)
    right_col = chr(ord('A') + right_col)
    if ord(right_col) >= ord('I'):
        old_right_col = right_col
        right_col = chr(ord(right_col) + 1)
        if verbose:
            print('right col was shifted from', old_right_col, 'to:', right_col)
    
    if verbose:
        print(left_col, upper_row, right_col, lower_row)
    assert left_col >= 'A'
    assert right_col <= 'T'
    assert right_col != 'I'
    assert upper_row >= 0 and upper_row < board_height
    assert lower_row >= 0 and lower_row < board_height
    
    processed_pattern = (pattern.replace('b', 'x').replace('w', 'o').
                         replace('=','').replace(' ', ''))
    result = (processed_pattern, board_width, board_height,
              left_col, upper_row + 1, right_col, lower_row + 1 )
    if verbose:
        print("result:", result)
    return result


def pattern_as_html(pattern):
    """
    Produces the complete HTML div needed to render a pattern in jgoboard.
    """
    (processed_pattern, board_size, board_size, left_col, upper_row, right_col,
     lower_row) = process_pattern_for_jgoboard(pattern)
    return ('<div class="jgoboard" data-jgosize="%sx%s"'
            'data-jgoview="%s%s-%s%s">\n%s\n</div>' % (
        board_size, board_size, left_col, upper_row, right_col, lower_row,
        processed_pattern))


def html_timeline_top_patterns_from_version(f,
                                            full_img_dir,
                                            relative_img_dir,
                                            imgcnt,
                                            version, 
                                            versions,
                                            version_ids,
                                            epoch_to_patterns,
                                            pattern_to_epochs,
                                            avoid_patterns,
                                            max_display_patterns,
                                            min_num_stones,
                                            max_num_stones,
                                            min_delta_colors,
                                            max_delta_colors,
                                            min_epochs_with_pattern,
                                            xticks='epochs'):
    """
    Find the most frequent patterns from a given version and generates HTML to
    show their popularity across all other versions.
    The generated HTML is written to the f file handle which is an already open,
    writable file.
    This is used in a loop, for several versions, so the file open/close is
    handled by the caller.
  
    For each pattern it outputs, it also generates a plot showing the pattern's
    frequency across various versions as a PNG file. Each such PNG file is
    written to the full_img_dir directory, and is reffered to in HTML via
    the relative_img_dir path, for instance as relative_img_dir/0.png, etc.

    versions: list of version ids in chronological order (for graphing purposes)
    
    max_delta_colors: max abs(num_black_stones-num_white_stones)
    
    <div class="jgoboard" data-jgosize="19x19" data-jgoview="M7-T1">
    ....
    oo.x
    .xxx
    ....
    </div>
    """
    
    print("Processing top patterns from", version,
        "min_num_stones", min_num_stones)
    patterns_in_epoch = sorted([x for x in epoch_to_patterns[version].items()
                                if x[0] not in avoid_patterns],
                               key=lambda x: x[1], reverse=True)

    display_patterns = []
    for pattern, count in patterns_in_epoch:
        assert pattern not in avoid_patterns
        if not is_pattern_acceptable(pattern, min_delta_colors, max_delta_colors, min_num_stones, max_num_stones):
            continue

        if len(pattern_to_epochs[pattern]) < min_epochs_with_pattern:
            # This pattern does not appear in enough epochs
            continue

        # If it occurs in only one epoch, make sure it does not occur only once, since that would
        # create a lot of noisy patterns
        if len(pattern_to_epochs[pattern]) == 1:
            ep = list(pattern_to_epochs[pattern].keys())[0]
            if epoch_to_patterns[ep][pattern] < 2:
                continue
        
        display_patterns.append(pattern)
        if len(display_patterns) >= max_display_patterns:
            break

    if display_patterns:
        f.write("<h1>Version %s</h1>\n" % version)

    for pattern in display_patterns:
        pattern_timeline = build_pattern_timeline(pattern,
                                                  pattern_to_epochs[pattern],
                                                  versions)
        f.write(pattern_as_html(pattern))
        f.write("\n")
        custom_figsize()
        plt.bar(range(len(versions)), pattern_timeline, color='blue')
        # plt.plot(pattern_timeline, color='blue')
        if xticks=='epochs':
            plt.xticks(range(len(pattern_count_by_version)), versions, rotation='vertical')
        plt.axvline(x=version_ids[version], color='red')
        
        imgfilename = os.path.join(full_img_dir, ("%s.png" % imgcnt))
        f.write("<div><img src=\"%s\"></div>\n" %
                ("%s/%s.png" % (relative_img_dir, imgcnt)))
        f.write("<div class=\"clrdiv\"></div>\n")
        imgcnt += 1
        plt.savefig(imgfilename, bbox_inches='tight')
        plt.close()
        avoid_patterns.add(pattern)
    return imgcnt


def html_timeline_top_patterns_global(
    f,
    full_img_dir,
    relative_img_dir,
    imgcnt,
    versions,
    pattern_to_epochs,
    popular_patterns,
    max_display_patterns,
    min_num_stones,
    max_num_stones,
    min_delta_colors,
    max_delta_colors,
    xticks='epochs'):
    """
    Find the most frequent global patterns and generates HTML to
    show their popularity across all other versions.
    The generated HTML is written to the f file handle which is an already open,
    writable file.
    This is used in a loop, for several versions, so the file open/close is
    handled by the caller.
  
    The plot showing the pattern's
    frequency across various versions is a PNG file. Each such PNG file is
    written to the full_img_dir directory, and is reffered to in HTML via
    the relative_img_dir path, for instance as relative_img_dir/0.png, etc.

    versions: list of version ids in chronological order (for graphing purposes)
    
    max_delta_colors: max abs(num_black_stones-num_white_stones)
    
    <div class="jgoboard" data-jgosize="19x19" data-jgoview="M7-T1">
    ....
    oo.x
    .xxx
    ....
    </div>
    """

    display_patterns = []
    for pattern, score in popular_patterns:
        if not is_pattern_acceptable(pattern, min_delta_colors, max_delta_colors, min_num_stones, max_num_stones):
            continue
        display_patterns.append(pattern)
        if len(display_patterns) >= max_display_patterns:
            break

    for pattern in display_patterns:
        pattern_timeline = build_pattern_timeline(pattern,
                                                  pattern_to_epochs[pattern],
                                                  versions)
        f.write(pattern_as_html(pattern))
        f.write("\n")
        custom_figsize()
        plt.bar(range(len(versions)), pattern_timeline, color='blue')
        if xticks =='epochs': 
            plt.xticks(range(len(pattern_count_by_version)), versions, rotation='vertical')
        
        imgfilename = os.path.join(full_img_dir, ("%s.png" % imgcnt))
        f.write("<div><img src=\"%s\"></div>\n" %
                ("%s/%s.png" % (relative_img_dir, imgcnt)))
        f.write("<div class=\"clrdiv\"></div>\n")
        imgcnt += 1
        plt.savefig(imgfilename, bbox_inches='tight')
        plt.close()
    return imgcnt


HTML_BEGIN = """
        <!DOCTYPE HTML>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <title>Go Patterns</title>
          <style>
            .jgoboard {
                float: left;
            }
            .clrdiv {
                clear: left;
            }
          </style>
        </head>
        <body>
        """

HTML_END = """
        <script type="text/javascript" src="dist/jgoboard-latest.js"></script>
        <script type="text/javascript" src="large/board.js"></script>
        <script type="text/javascript" src="medium/board.js"></script>
        <script type="text/javascript">JGO.auto.init(document, JGO);</script>
        </body>
        </html>
        """

def generate_patterns_frequency_html(
    versions,
    pattern_count_by_version, 
    pattern_frequency_in_epochs,
    outputdir,
    display_global=True,
    display_by_version=True,
    max_display_patterns_global=30,
    max_display_patterns_per_version=3,
    unique_patterns=True,
    min_num_stones=10,
    max_num_stones=10,
    min_delta_colors=1,        
    max_delta_colors=1,
    min_epochs_with_pattern=2,
    xticks='epochs',
    html_filename="patterns.html",
    imgdir="img"):
    """
    Creates outputdir and outputdir/imgdir paths. Fails if already exisits.
    Writes HTML file to outputdir/html_filename and writes images for plots
    to outputdir/imgdir/0.png, outputdir/imgdir/1.png, etc.
    """
    full_imgdir = os.path.join(outputdir, imgdir)
    os.makedirs(full_imgdir)
    f = open(os.path.join(outputdir, html_filename), 'w')
    f.write(HTML_BEGIN)  

    version_ids = {}
    for (i, v) in enumerate(list(versions)):
        version_ids[v] = i
    
    popular_patterns = sorted([(p, sum([k[1] for k in pattern_frequency_in_epochs[p].items()]))
                               for p in pattern_frequency_in_epochs.keys()],
                               key=lambda x: x[1],
                               reverse=True)

    imgcnt = 0

    if display_global:
        imgcnt = html_timeline_top_patterns_global(
            f,
            full_imgdir,
            imgdir,
            imgcnt,
            versions,
            pattern_frequency_in_epochs,
            popular_patterns,
            max_display_patterns_global,
            min_num_stones,
            max_num_stones,
            min_delta_colors,
            max_delta_colors,
            xticks)

    if display_by_version:
        avoid_patterns = None
        if unique_patterns:
            avoid_patterns = set()
        for v in versions:
            imgcnt = html_timeline_top_patterns_from_version(
                f,
                full_imgdir,
                imgdir,
                imgcnt,
                v,
                versions,
                version_ids,
                pattern_count_by_version, 
                pattern_frequency_in_epochs,
                avoid_patterns,
                max_display_patterns_per_version,
                min_num_stones,
                max_num_stones,
                min_delta_colors,
                max_delta_colors,
                min_epochs_with_pattern,
                xticks)

    f.write(HTML_END)
    f.close()

