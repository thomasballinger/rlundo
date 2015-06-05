#!/usr/bin/env python
"""
memory_monitor

Tool to generate and graph real time records of the memory usage.

From the command line:
    `python memory_monitor.py`

To exit:
    Ctrl+c
"""

from __future__ import unicode_literals
import matplotlib.pyplot as plt
import numpy as np
from subprocess import Popen, PIPE


def generate_memory_stats(interval=0.1, count=None):
    """Create a generator of the current free memory in the system.

    Args:
        interval: Interval in seconds to generate new memory records.
        count: Optional maximum records to generate.
    """

    # generate a maximum of 'count' records
    if count:
        p = Popen(['vm_stat', '-c', unicode(count), unicode(interval)],
                  stdout=PIPE)

    # generate infinite records
    else:
        p = Popen(['vm_stat', unicode(interval)], stdout=PIPE)

    # yield records until keybord interruption or 'count' reached
    try:
        while True:
            line = p.stdout.readline()
            if 'Mach' not in line and 'free' not in line:
                yield unicode(line.split()[0])

    except KeyboardInterrupt:
        print("\nMemory usage monitor exited!\n")


def graph_memory_usage():
    """Create a real time graph of the free memory in the system."""

    x = np.linspace(0, 50, 1000)
    y = np.linspace(0, 1, 1000)

    # TODO: scale should be the total memory in the system
    scale = int(generate_memory_stats().next())
    if scale < 1600000:
        scale = 1600000
    y[0] = scale

    plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1, = ax.plot(x, y, 'r-')  # Returns a tuple of line objects

    xmin, xmax = 0, 50
    ymin, ymax = 0, scale * 1.1  # give some room to appreciate better the line
    plt.axis([xmin, xmax, ymin, ymax])

    try:
        for record in generate_memory_stats():
            y = np.append(y[1:], record)
            line1.set_ydata(y)
            fig.canvas.draw()

    except KeyboardInterrupt:
        print("Memory graph exited")


if __name__ == '__main__':
    graph_memory_usage()
