"""
rewrite runs a command as a subprocess, and has an api for saving
terminal state.

Opening a connection to localhost:4242 will save the current state
Opening a connection to localhost:4243 will restore the state as it
was two saved states ago.
"""

import argparse
import locale
import logging
import os
import re
import socket
import sys
import tempfile
import threading
import time

import blessings

import pity
from findcursor import get_cursor_position

# version 1: record sequences, guess how many lines to go back up
terminal = blessings.Terminal()
encoding = locale.getdefaultlocale()[1]

outputs = [b'']
terminal_output_lock = pity.TerminalLock()
stdin_lock = threading.Lock()


logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', level=logging.INFO)


def temp_name(s):
    name = os.path.join(tempfile.gettempdir(), str(os.getpid()) + s)
    if os.path.exists(name):
        os.remove(name)
    if ' ' in name:
        raise ValueError('Things will fall apart if temp files have spaces in them: %r' % name)
    return name

def write(data):
    sys.stdout.write(data)
    sys.stdout.flush()


def save():
    time.sleep(.001)
    # correct way to do this would be to
    # wait until there's nothing to read on the pty

    outputs.append(b'')
    logger.info('full output stack: %r' % (outputs, ))


def count_lines(msg, width):
    """Number of lines msg would move cursor down at a terminal width"""
    resized_lines = [_rows_required(line, width) for line in msg.split('\n')]
    num_lines = sum(resized_lines) - 1
    return num_lines


def _visible_characters(line):
    """Number of characters in string without color escape characters."""
    line_without_colours = re.sub("\x1b[[]0(;\d\d)?m", "", line)
    line_without_colours = line_without_colours.strip("\n")
    return len(line_without_colours)


def _rows_required(line, width):
    """Calculate how many rows a line will need to be printed"""
    return max(0, (_visible_characters(line) - 1) // width) + 1


def linesplit(lines, width):
    rows = []
    for line in lines:
        rows.extend(line[i:i + width] for i in range(0, len(line), width))
    return rows


def history(sequences):
    full = b''.join(sequences)
    return full.split(b'\n')

HISTORY_BROKEN_MSG = '#<---History contiguity broken by rewind--->'


def restore():
    with terminal_output_lock:
        _restore()

def _restore():
    logger.debug('full output stack: %r' % (outputs, ))
    lines_between_saves = outputs.pop() if outputs else ''
    lines_after_save = outputs.pop() if outputs else ''
    lines = lines_between_saves + lines_after_save
    logger.info('lines to rewind: %r' % (lines, ))
    n = count_lines(lines.decode(encoding), terminal.width)
    logger.info('numer of lines to rewind %d' % (n, ))
    with stdin_lock:
        lines_available, _ = get_cursor_position(sys.stdout, sys.stdin)
    logger.debug('lines move: %d lines_available: %d' % (n, lines_available))
    if n > lines_available:
        for _ in range(200):
            write(terminal.move_left)
        write(terminal.clear_eol)
        for _ in range(lines_available):
            write(terminal.move_up)
            write(terminal.clear_eol)
        write(HISTORY_BROKEN_MSG[:terminal.width])
        write('\n')
        for _ in range(terminal.height - 2):
            write(terminal.move_down)
        for _ in range(200):
            write(terminal.move_left)
        write('\n')
        for _ in range(terminal.height - 1):
            write(terminal.move_up)
        middle = terminal.height // 2

        for line in history(''.join(outputs))[:-1][-middle:]:
            write(line + '\r\n')

    else:
        logger.debug('moving cursor %d lines up for %r' % (n, lines))
        for _ in range(n):
            write(terminal.move_up)
        for _ in range(200):
            write(terminal.move_left)
        write(terminal.clear_eos)


def set_up_listener(handler, addr):
    def forever():
        while True:
            conn, addr = sock.accept()
            handler()
            conn.close()

    sock = socket.socket(family=socket.AF_UNIX)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(1)
    t = threading.Thread(target=forever)
    t.daemon = True
    t.start()
    return sock, t


def master_read(fd):
    data = os.read(fd, 1024)
    logger.info('read data: %r' % data)
    if outputs:
        outputs[-1] += data
    return data


def stdin_read(fd):
    with stdin_lock:
        data = os.read(fd, 1024)
        logger.info('read from stdin: %r' % data)
        return data


def run(argv):
    pity.spawn(argv,
               master_read=master_read,
               stdin_read=stdin_read,
               handle_window_size=True,
               terminal_output_lock=terminal_output_lock)


def run_with_listeners(args, save_addr=None, restore_addr=None):
    if save_addr is None:
        save_addr = temp_name('save')
    if restore_addr is None:
        restore_addr = temp_name('restore')
    listeners = [set_up_listener(save, save_addr),
                 set_up_listener(restore, restore_addr)]
    os.environ["RLUNDO_SAVE"] = save_addr
    os.environ["RLUNDO_RESTORE"] = restore_addr
    run(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run a command in a pty, saving and restoring the terminal state")
    parser.add_argument('--save-addr', action='store', default=None)
    parser.add_argument('--restore-addr', action='store', default=None)
    parser.add_argument('command', nargs='*')
    args = parser.parse_args()
    if args.command == []:
        args.command = ['python', '-c', "while True: raw_input('>')"]
    run_with_listeners(args.command, save_addr=args.save_addr, restore_addr=args.restore_addr)
