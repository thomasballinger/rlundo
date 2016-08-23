import builtins

from .. import undoreadline


def start_undoable_adventure():
    undoreadline.monkeypatch_input_no_rewrite()
    import adventure.__main__


if __name__ == '__main__':
    start_undoable_adventure()
