import os
import socket
import sys
import threading
import logging

import blessings
from termcast_client import pity

# version 1: record sequences, guess how many lines to go back up
terminal = blessings.Terminal()

outputs = ['']

logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', level=logging.DEBUG)


def write(data):
    sys.stdout.write(data)
    sys.stdout.flush()


def save():
    outputs.append('')
    logger.debug('full output stack: %r' % (outputs, ))


def count_lines(msg):
    return msg.count('\n')


def restore():
    logger.debug('full output stack: %r' % (outputs, ))
    lines = outputs.pop() if outputs else ''
    lines += outputs.pop() if outputs else ''
    n = count_lines(lines)
    logger.debug('moving cursor %d lines up for %r' % (n, lines))
    for _ in range(n):
        write(terminal.move_up)
    for _ in range(200):
        write(terminal.move_left)
    write(terminal.clear_eos)


def set_up_listener(handler, port):
    def forever():
        while True:
            conn, addr = sock.accept()
            handler()
            conn.close()

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', port))
    sock.listen(1)
    t = threading.Thread(target=forever)
    t.daemon = True
    t.start()
    return sock, t


def master_read(fd):
    data = os.read(fd, 1024)
    if outputs:
        outputs[-1] += data
    return data


def run(argv):
    pity.spawn(argv,
               master_read=master_read,
               handle_window_size=True)


def run_with_listeners(args):
    listeners = [set_up_listener(save, 4242), set_up_listener(restore, 4243)]
    run(args)


if __name__ == '__main__':
    run_with_listeners(sys.argv[1:] if sys.argv[1:] else ['python', '-c', "while True: raw_input('>')"])
