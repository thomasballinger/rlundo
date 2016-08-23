"""Alternate interpreters to use that follow the rlundo protocol.

useful if an interpreter does not dynamically load readline.c
in an easily interceptable way"""

import os


def is_python(path):
    return os.path.basename(path) == "python"


def is_ipython(path):
    """Check if the terminal to be opened is ipython."""
    return os.path.basename(path) == "ipython"

def is_adventure(path):
    return path == 'adventure'

def is_adventure_no_rewrite(path):
    return path == 'adventure_no_rewrite'


from . import undoablepython
from . import undoableipython

interpreters = [
    (['python3', '-m', 'rlundo.interps.undoableadventurenorewrite'], is_adventure_no_rewrite),
    (['python3', '-m', 'rlundo.interps.undoableadventure'], is_adventure),
    (['python', os.path.abspath(undoablepython.__file__)], is_python),
    (['python', os.path.abspath(undoableipython.__file__)], is_ipython),
]
