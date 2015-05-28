from __future__ import unicode_literals


import os
import pity

outputs = ['']


def master_read(fd):
    data = os.read(fd, 1024)
    if outputs:
        outputs[-1] += data
    return data


def interactive():
    pity.spawn(['python', '-c', 'while True: raw_input()'],
               master_read=master_read,
               handle_window_size=True)
    print outputs


if __name__ == '__main__':
    interactive()
