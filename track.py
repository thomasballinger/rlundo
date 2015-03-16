import sys
import random
import time
import re
import termios
import tty
import threading
from collections import namedtuple

import vt100
from termcast_client import Client
import blessings

#Based heavily off of the work of doy, github.com/doy

#TODO get initial cursor position, call it 

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
            except IOError:
                raise ValueError('cursor get pos response read interrupted')

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


class Terminal(object):
    def __init__(self, cursor_row):
        self.t = blessings.Terminal()
        self.initial_top_usable_row = cursor_row
        self.w = self.t.width
        self.h = self.t.height
        self.vt = vt100.vt100(self.h, self.w)
        self.vt.process(self.t.move(self.initial_top_usable_row, 1))
        self.prev_read = ''

    def write(self, data):
        self.stdout.write(data)
        self.stdout.flush()

    def send(self, data):
        to_process = self.prev_read + data
        processed = self.vt.process(to_process)
        self.prev_read = to_process[processed:]
        return len(data)

    @property
    def top_usable_row(self):
        """zero-indexed top line of terminal we can write to"""
        return max(0, self.initial_top_usable_row - self.scroll_offset)

    @property
    def scroll_offset(self):
        return self.vt._screen._scroll_offset

    def render(self, state):
        #TODO restore cursor position
        #TODO account for scroll_offset
        lines, cursor_pos, scroll_offset = state
        lines_to_render = lines[self.top_usable_row:]
        with self.t.location(x=0, y=self.top_usable_row):
            sys.stdout.write(self.t.clear_eol)
            sys.stdout.write(re.sub(r'[a-z]',
                lambda m: m.group().swapcase() if random.random() < .5 else m.group(),
                ('\n\r'+self.t.clear_eol).join(lines_to_render).replace('Python', self.status)))
        sys.stdout.flush()

    def snapshot(self):
        return TerminalState(
            lines=self.vt.window_contents().splitlines(),
            cursor_pos=self.vt.cursor_position(),
            scroll_offset=self.vt._screen._scroll_offset)

    @property
    def status(self):
        return "top usable row: %d offset: %d" % (self.top_usable_row, self.scroll_offset)

TerminalState = namedtuple('TerminalState', [
    'lines',          # list of lines
    'cursor_pos',     # where the cursor was, (line, col) out of lines
    'scroll_offset',  # how many times vt100 had scrolled at that point
    ])


class LocalClient(Client):
    def __init__(self, term):
        self.sock = term

    def _new_socket(self):
        pass

    def _renew_socket(self):
        pass


def main():
    def render_sometimes():
        while True:
            old = terminal.snapshot()
            time.sleep(1.8)
            terminal.render(old)
            time.sleep(.2)
            terminal.render(terminal.snapshot())
    t = threading.Thread(target=render_sometimes)
    t.daemon = True

    start_row, _ = get_cursor_position(sys.stdout, sys.stdin)
    terminal = Terminal(cursor_row=start_row)
    client = LocalClient(terminal)
    t.start()
    client.run(sys.argv[1:])

if __name__ == '__main__':
    main()
