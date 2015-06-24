"""Alternate interpreters to use that follow the rlundo protocol.

useful if an interpreter does not dynamically load readline.c
in an easily interceptable way"""

import os


def is_python(path):
    return os.path.basename(path) == "python"


def is_ipython(path):
    """Check if the terminal to be opened is ipython."""
    return os.path.basename(path) == "ipython"

from . import undoablepython
from . import undoableipython

interpreters = [
    (['python', os.path.abspath(undoablepython.__file__)], is_python),
    (['python', os.path.abspath(undoableipython.__file__)], is_ipython),
]
