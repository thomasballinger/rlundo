#!/usr/bin/env python
import sys

from rlundoable import modify_env_with_modified_rl
from rewrite import run_with_listeners
import undoablepython
import undoableipython


def start_undoable_rl(args):

    if undoablepython.rl_is_python(args[1]):
        undoablepython.start_undoable_python(sys.argv[1:])

    elif undoableipython.rl_is_ipython(args[1]):
        undoableipython.start_undoable_ipython(sys.argv[1:])

    else:
        modify_env_with_modified_rl()
        run_with_listeners(args[1:])


if __name__ == "__main__":
    start_undoable_rl(sys.argv)
