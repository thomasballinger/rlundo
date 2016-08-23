import code
import os
import sys

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
    builtins.input = readline


def readline(prompt):
    global WRITE_TO_PARENT_FD

    while True:
        try:
            s = orig_input(prompt)
        except EOFError:
            die_and_tell_parent(b'exit')

        if s == 'undo':
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


def die_and_tell_parent(msg):
    if WRITE_TO_PARENT_FD is not None:
        os.write(WRITE_TO_PARENT_FD, msg+b'\n')
    sys.exit()


class ForkUndoConsole(code.InteractiveConsole):
    def raw_input(self, prompt=""):
        return readline(prompt)

    def input(self, prompt=""):
        return readline(prompt)


if __name__ == '__main__':
    console = ForkUndoConsole()
    console.interact()
