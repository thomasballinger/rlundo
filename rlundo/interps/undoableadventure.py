import sys

import builtins

from .. import undoreadline


def start_undoable_adventure():
    undoreadline.monkeypatch_readline()
    import adventure.__main__


if __name__ == '__main__':
    start_undoable_adventure()
