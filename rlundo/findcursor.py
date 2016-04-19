import termios
import tty
import re


class Cbreak(object):

    def __init__(self, stream):
        self.stream = stream

    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream, termios.TCSANOW)
        return Termmode(self.stream, self.original_stty)

    def __exit__(self, *args):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)


class Termmode(object):

    def __init__(self, stream, attrs):
        self.stream = stream
        self.attrs = attrs

    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        termios.tcsetattr(self.stream, termios.TCSANOW, self.attrs)

    def __exit__(self, *args):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)


def get_cursor_position(to_terminal, from_terminal):
    with Cbreak(from_terminal):
        return _inner_get_cursor_position(to_terminal, from_terminal)


def _inner_get_cursor_position(to_terminal, from_terminal):
    query_cursor_position = u"\x1b[6n"
    to_terminal.write(query_cursor_position)
    to_terminal.flush()

    def retrying_read():
        while True:
            try:
                c = from_terminal.read(1)
                if c == '':
                    raise ValueError("Stream should be blocking - should't"
                                     " return ''. Returned %r so far", (resp,))
                return c
            except IOError as e:
                raise ValueError('cursor get pos response read interrupted: %r' % (resp, ))

    resp = ''
    while True:
        c = retrying_read()
        resp += c
        m = re.search('(?P<extra>.*)'
                      '(?P<CSI>\x1b\[|\x9b)'
                      '(?P<row>\\d+);(?P<column>\\d+)R', resp, re.DOTALL)
        if m:
            row = int(m.groupdict()['row'])
            col = int(m.groupdict()['column'])
            extra = m.groupdict()['extra']
            if extra:  # TODO send these to child process
                raise ValueError(("Bytes preceding cursor position "
                                  "query response thrown out:\n%r\n"
                                  "Pass an extra_bytes_callback to "
                                  "CursorAwareWindow to prevent this")
                                 % (extra,))
            return (row - 1, col - 1)

