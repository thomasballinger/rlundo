import errno
import fcntl
import os
import pty
import select
import signal
import sys
import termios
import threading
import tty
import logging
logging.basicConfig(filename='debug.log', level=logging.INFO)
from .termhelpers import Nonblocking

class TerminalLock(object):
    """Lock that can be over-released

    Every master write to the pty should be followed
    by a pty write to the terminal, but not every pty write
    is initiated by a master write."""

    def __init__(self):
        self.rlock = threading.RLock()
        self.lock_count = 0

    def acquire(self):
        self.rlock.acquire()
        self.lock_count += 1

    def release(self):
        if self.lock_count > 0:
            self.rlock.release()
            self.lock_count -= 1

    def __enter__(self):
        return self.rlock.__enter__()

    def __exit__(self, *args, **kwargs):
        return self.rlock.__exit__(*args, **kwargs)



CHILD = pty.CHILD
STDIN_FILENO = pty.STDIN_FILENO
STDOUT_FILENO = pty.STDOUT_FILENO
STDERR_FILENO = pty.STDERR_FILENO

def fork(handle_window_size=False):
    # copied from pty.py, with modifications
    master_fd, slave_fd = openpty()
    slave_name = os.ttyname(slave_fd)
    pid = os.fork()
    if pid == CHILD:
        # Establish a new session.
        os.setsid()
        os.close(master_fd)

        if handle_window_size:
            clone_window_size_from(slave_name, STDIN_FILENO)

        # Slave becomes stdin/stdout/stderr of child.
        os.dup2(slave_fd, STDIN_FILENO)
        os.dup2(slave_fd, STDOUT_FILENO)
        os.dup2(slave_fd, STDERR_FILENO)
        if (slave_fd > STDERR_FILENO):
            os.close (slave_fd)

        # Explicitly open the tty to make it become a controlling tty.
        tmp_fd = os.open(os.ttyname(STDOUT_FILENO), os.O_RDWR)
        os.close(tmp_fd)
    else:
        os.close(slave_fd)

    # Parent and child process.
    return pid, master_fd, slave_name


def openpty():
    return pty.openpty()

def _copy(master_fd, master_read=pty._read, stdin_read=pty._read,
          terminal_output_lock=None):
    """Parent copy loop.
    Copies
            pty master -> standard output   (master_read)
            standard input -> pty master    (stdin_read)"""
    logging.debug('starting _copy loop')
    fds = [master_fd, STDIN_FILENO]
    while True:
        logging.debug('calling select in copy')
        rfds, wfds, xfds = select.select(fds, [], [])
        logging.debug('select call in copy finished! %r %r %r' % (rfds, wfds, xfds, ))
        if master_fd in rfds:
            logging.debug('master_fd is ready, so calling read')
            data = master_read(master_fd)
            logging.debug('master_fd master_read call done, got data: %r' % (data, ))
            if not data:  # Reached EOF.
                fds.remove(master_fd)
            else:
                os.write(STDOUT_FILENO, data)
                if terminal_output_lock is not None:
                    terminal_output_lock.release()

        if STDIN_FILENO in rfds:
            logging.debug('stdin is ready, dealing...')

            with Nonblocking(STDIN_FILENO):
                try:
                    data = stdin_read(STDIN_FILENO)
                except OSError as e:
                    if e[0] != errno.EAGAIN:
                        raise
                else:
                    if not data:
                        fds.remove(STDIN_FILENO)
                    else:
                        if terminal_output_lock is not None:
                            terminal_output_lock.acquire()
                        pty._writen(master_fd, data)
            logging.debug('done dealing with stdin')

def spawn(argv, master_read=pty._read, stdin_read=pty._read, handle_window_size=False,
          terminal_output_lock=None):
    # copied from pty.py, with modifications
    # note that it references a few private functions - would be nice to not
    # do that, but you know
    if type(argv) == type(''):
        argv = (argv,)
    pid, master_fd, slave_name = fork(handle_window_size)
    if pid == CHILD:
        os.execlp(argv[0], *argv)
    try:
        mode = tty.tcgetattr(STDIN_FILENO)
        tty.setraw(STDIN_FILENO)
        restore = 1
    except tty.error:    # This is the same as termios.error
        restore = 0

    if handle_window_size:
        signal.signal(
            signal.SIGWINCH,
            lambda signum, frame: _winch(slave_name, pid)
        )

    while True:
        try:
            _copy(master_fd, master_read, stdin_read, terminal_output_lock)
        except OSError as e:
            if e.errno == errno.EINTR:
                continue
            if restore:
                tty.tcsetattr(STDIN_FILENO, tty.TCSAFLUSH, mode)
        except select.error as e:
            if not sys.version_info.major == 2:  # in Python 2 EINTR is a select.error
                raise
            if e[0] == errno.EINTR:
                continue
            raise
        break

    os.close(master_fd)
    return os.waitpid(pid, 0)[1]

def clone_window_size_from(slave_name, from_fd):
    slave_fd = os.open(slave_name, os.O_RDWR)
    try:
        fcntl.ioctl(
            slave_fd,
            termios.TIOCSWINSZ,
            fcntl.ioctl(from_fd, termios.TIOCGWINSZ, " " * 1024)
        )
    finally:
        os.close(slave_fd)

def _winch(slave_name, child_pid):
    clone_window_size_from(slave_name, STDIN_FILENO)
    os.kill(child_pid, signal.SIGWINCH)
