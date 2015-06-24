#!/usr/bin/env python

"""
rlundo

Start a repl with undo feature.
"""

from __future__ import unicode_literals
import sys

from rlundoable import modify_env_with_modified_rl
from termrewrite import run_with_listeners

import interps

def start_undoable_rl(args):
    for command, predicate in interps.interpreters:
        if predicate(args[1]):
            return run_with_listeners(command + args[2:])
    else:
        modify_env_with_modified_rl()
        run_with_listeners(args[1:])


if __name__ == "__main__":
    start_undoable_rl(sys.argv)
