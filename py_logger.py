#!/usr/bin/env python

"""
py_logger

Write a log of what's what bytes are being written by a command

Use it from the command line: `python py_logger.py ipython`
Use it from another python script:
    `from py_logger import run`
    `run(['ipython'])
"""

from __future__ import unicode_literals
import os
import sys

import pity

log = open('output.log', 'w')


def master_read(fd):
    """Read the output of a terminal writing a log in the middle.
    Args:
        fd: File descriptor being read.
    """
    data = os.read(fd, 1024)
    log.write(data)
    return data


def run(argv):
    """Spawn a process with master read writing a log file in between.
    Args:
        argv: Additional arguments after `python py_logger` command
    """
    pity.spawn(argv,
               master_read=master_read,
               handle_window_size=True)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("To record what bytes ipython writes to stdout/stderr:")
        print("python py_logger.py ipython")
    else:
        run(sys.argv[1:])
