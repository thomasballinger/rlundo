#!/usr/bin/env python

import code
import logging
import os
import socket
import sys
from functools import partial

# read about copy-on-write for Python processes - I feel like I've heard
# this doesn't work well

py2 = False
if sys.version_info.major == 2:
    input = raw_input
    ConnectionRefusedError = socket.error
    py2 = True

logger = logging.getLogger(__name__)

DEBUG = False

print('running with pid %r' % (os.getpid(),))


def connect_and_wait_for_close(addr):
    s = socket.socket(family=socket.AF_UNIX)
    try:
        s.connect(addr)
    except ConnectionRefusedError:
        pass
    else:
        assert b'' == s.recv(1024)


save = partial(connect_and_wait_for_close, addr=os.environ['RLUNDO_SAVE'])
restore = partial(connect_and_wait_for_close, addr=os.environ['RLUNDO_RESTORE'])


def log(msg):
    if DEBUG:
        logger.debug(str(os.getpid()) + ': ' + str(msg) + '\n')


def readline(prompt):
    """Get input from user, fork or exit

    readline needs function attributes:
    .on_close() should notify parent process we're undoing
    .on_exit() should notify parent that we're exiting"""

    log('pid %r initial call to readline' % (os.getpid()))
    while True:
        save()
        try:
            s = input(prompt)
        except EOFError:
            readline.on_exit()
        except KeyboardInterrupt:
            s = 'undo'
        if s == 'undo':
            restore()
            readline.on_undo()
        read_fd, write_fd = os.pipe()
        pid = os.fork()
        is_child = pid == 0
        log('created read/write fd pair: %r %r' % (read_fd, write_fd))

        if is_child:

            def on_undo():
                log('undoing command')
                log('writing line to say done on fd %r' % (write_fd,))
                os.write(write_fd, b'done\n')
                log('wrote, exiting')
                sys.exit()

            def on_exit():
                log('exiting!')
                os.write(write_fd, b'exit\n')
                sys.exit()

            readline.on_undo = on_undo
            readline.on_exit = on_exit

            log('child returning to loop')
            return s
        else:
            log('Waiting for child %r by reading on fd %r' % (pid, read_fd))
            from_child = os.read(read_fd, 1)
            if from_child == b'e':
                readline.on_exit()
            log('parent %r received response from child %r: %r' %
                (os.getpid(), pid, from_child))
            continue


readline.on_undo = sys.exit
readline.on_exit = sys.exit


class ForkUndoConsole(code.InteractiveConsole):

    def raw_input(self, prompt=""):
        """Write a prompt and read a line.

        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.

        The base implementation uses the built-in function
        raw_input(); a subclass may replace this with a different
        implementation.

        """
        return readline(prompt)


def rl_is_python(rl_path):
    return os.path.basename(rl_path) == "python"


def start_undoable_python(args=None):
    console = ForkUndoConsole()

    if args:
        sys.argv = args

    console.interact()


if __name__ == '__main__':
    start_undoable_python()
