import fcntl
import os
import termios
import tty


class Cbreak(object):
    def __init__(self, stream):
        self.stream = stream

    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream, termios.TCSANOW)

    def __exit__(self, *args):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)


class Nonblocking(object):

    def __init__(self, fd):
        self.fd = fd

    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)

    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)


