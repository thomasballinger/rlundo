import random
import re
import socket
import sys
import threading
import time
import signal
from collections import namedtuple

import vt100
from termcast_client import Client
import blessings
from findcursor import get_cursor_position

#Based heavily off of the work of doy, github.com/doy

#TODO get initial cursor position, call it 


class Terminal(object):
    def __init__(self, cursor_row):
        self.t = blessings.Terminal()
        self.initial_top_usable_row = cursor_row
        self.w = self.t.width
        self.h = self.t.height
        self.vt = vt100.vt100(self.h, self.w)
        self.vt.process(self.t.move(self.initial_top_usable_row, 1))
        self.prev_read = ''
        self.stack = [self.snapshot()]
        self.sequences_since_last_save = ''
        self.set_up_listeners()

    def set_up_listeners(self):
        self.save = socket.socket()
        self.save.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.save.bind(('localhost', 4242))
        self.save.listen(1)
        self.undo = socket.socket()
        self.undo.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.undo.bind(('localhost', 4243))
        self.undo.listen(1)

    def go_back(self):
        self.stack.pop()
        old = self.stack[0]
        self.render(old)

    def wait_for_save(self):
        while True:
            self.save.accept()
            self.stack.append((self.snapshot(), self.sequence_since_last_save))
            self.sequence_since_last_save = ''

    def wait_for_undo(self):
        while True:
            self.undo.accept()
            self.go_back()

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
        self.vt.process(self.t.move(*cursor_pos))
        sys.stdout.write(self.t.move(*cursor_pos))
        sys.stdout.flush()

    def snapshot(self):
        return TerminalState(
            lines=self.vt.window_contents().splitlines(),
            cursor_pos=self.vt.cursor_position(),
            scroll_offset=self.vt._screen._scroll_offset)

    @property
    def status(self):
        return "stack height: %d offset: %d" % (len(self.stack), self.scroll_offset)

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

    start_row, _ = get_cursor_position(sys.stdout, sys.stdin)
    terminal = Terminal(cursor_row=start_row)
    client = LocalClient(terminal)

    t1 = threading.Thread(target=render_sometimes)
    t1.daemon = True
    t2 = threading.Thread(target=terminal.wait_for_push)
    t2.daemon = True
    t3 = threading.Thread(target=terminal.wait_for_pop)
    t3.daemon = True

    #t1.start()
    #t2.start()
    #t3.start()
    client.run(sys.argv[1:])

if __name__ == '__main__':
    main()
