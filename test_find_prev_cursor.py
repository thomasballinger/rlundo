"""Testing finding the location of the cursor"""
# Tests:
#  We don't have to predict resize patterns anymore.
#  Instead: Resize something and add some text.
#  Given 2 terminal states and the characters it took to get from one to the other
#    play back keypresses from initial state
#    manually linewrap that and count how many rows added
#    check that that's the old cursor position

import unittest
from terminal_dsl import divide_term_states, parse_term_state


'''
def find_prev_cursor_pos(diagram, sequence):
    snap1, snap2, result = [parse_term_state(
        x) for x in divide_term_states(diagram)]
    print snap1, snap2, result



class TestResizing(unittest.TestCase):
    def test_linwrap_in_history(self):
        find_prev_cursor_pos("""
        +---------+         +----------+         +----------+
        |georgiann+         |georgianna|         |georgianna|
        |a        !         |          |         |          |
        |         !         |hello     |         |hello     |
        +---------+    +    +----------+   -->   +----------+
        |hello    |         |$.track   |         |$.track   |
        |$.track  |         |>.1.+.1   |         |>.1.+.1   |
        |>.1.+.1  |         |2         |         |2         |
        |2        |         |> 3.+.4   |         |@         |
        |@        |         |7         |         |          |
        |         |         |@         |         |          |
        +---------+         +----------+         +----------+
        """, "3 + 4\n\r7\n\r")
'''



# check that last two terminals have same dimensions
# ignore first
# playing process in blank terminal should give reverse of diff of 1 and 2
# 


#   Grander plan: use diagrams to describe the way that tmux window will be
#   modified!
#
#   Plan for now: just send keys and use 


