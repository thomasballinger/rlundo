import sys

import vt100
from termcast_client import Client
import blessings

#Based heavily off of the work of doy, github.com/doy


class Terminal(object):
    def __init__(self):
        t = blessings.Terminal()
        w = t.width
        h = t.height
        self.vt = vt100.vt100(t.height, t.width)
        self.prev_read = ''
    def send(self, data):
        to_process = self.prev_read + data
        processed = self.vt.process(to_process)
        self.prev_read = to_process[processed:]
        return len(data)

class LocalClient(Client):
    def __init__(self, term):
        self.sock = term

    def _new_socket(self):
        pass

    def _renew_socket(self):
        pass

def main():
    terminal = Terminal()
    client = LocalClient(terminal)
    client.run(['python'])

if __name__ == '__main__':
    main()
