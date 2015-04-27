#!/usr/bin/env python
import sys
import os

from rlundoable import modify_env_with_modified_rl
from rewrite import run_with_listeners
import undoablepython
import undoableipython


def start_undoable_rl(args):

    if undoablepython.rl_is_python(args[1]):
        commands = ["python", "rewrite.py", "python", "undoablepython.py"]
        commands.extend(args[2:])
        os.system(" ".join(commands))

    elif undoableipython.rl_is_ipython(args[1]):
        commands = ["python", "rewrite.py", "python", "undoableipython.py"]
        commands.extend(args[2:])
        os.system(" ".join(commands))

    else:
        modify_env_with_modified_rl()
        run_with_listeners(args[1:])


if __name__ == "__main__":
    start_undoable_rl(sys.argv)
