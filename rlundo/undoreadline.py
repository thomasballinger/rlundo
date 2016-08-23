import code
import socket
import os
import sys
from functools import partial

# if this process is a child, this will change from None
WRITE_TO_PARENT_FD = None


py2 = False
if sys.version_info[0] == 2:
    py2 = True
    input = raw_input

# sometimes readline will be swapped out for builtins.input
orig_input = input


def monkeypatch_input_no_rewrite():
    import builtins
    builtins.input = readline_no_rewrite


def monkeypatch_readline():
    import builtins
    builtins.input = readline_no_rewrite
    init_terminal_rewriting()


def readline_no_rewrite(prompt):
    global WRITE_TO_PARENT_FD

    while True:
        save()
        try:
            s = orig_input(prompt)
        except EOFError:
            die_and_tell_parent(b'exit')

        if s == 'undo':
            restore()
            die_and_tell_parent(b'undo')
        read_fd, write_fd = os.pipe()
        pid = os.fork()
        is_child = pid == 0

        if is_child:
            WRITE_TO_PARENT_FD = write_fd
            return s
        else:
            from_child = os.read(read_fd, 1)
            if from_child == b'e':
                die_and_tell_parent(b'exit')
            continue


def save():
    pass


def restore():
    pass


def init_terminal_rewriting():
    global save
    global restore
    try:
        save = partial(connect_and_wait_for_close, addr=os.environ['RLUNDO_SAVE'])
        restore = partial(connect_and_wait_for_close, addr=os.environ['RLUNDO_RESTORE'])
    except KeyError:
        print(sorted(os.environ.keys()))
        raise


def connect_and_wait_for_close(addr):
    s = socket.socket(family=socket.AF_UNIX)
    try:
        s.connect(addr)
    except ConnectionRefusedError:
        pass
    else:
        assert b'' == s.recv(1024)


def die_and_tell_parent(msg):
    if WRITE_TO_PARENT_FD is not None:
        os.write(WRITE_TO_PARENT_FD, msg+b'\n')
    sys.exit()


class ForkUndoConsole(code.InteractiveConsole):
    def raw_input(self, prompt=""):
        return readline_no_rewrite(prompt)

    def input(self, prompt=""):
        return readline_no_rewrite(prompt)


if __name__ == '__main__':
    console = ForkUndoConsole()
    console.interact()
