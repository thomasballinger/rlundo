from functools import partial
import sys
import tempfile
import time

import tmuxp

py2 = sys.version_info.major == 2


def all_contents(pane):
    return pane.cmd('capture-pane', '-epS', '-10000').stdout


def all_lines(pane):
    return pane.cmd('capture-pane', '-epJS', '-10000').stdout


def scrollback(pane):
    all = all_contents(pane)
    return all[:len(all)-len(visible(pane))]


def visible(pane):
    return pane.cmd('capture-pane', '-ep').stdout


def visible_without_formatting(pane):
    return pane.cmd('capture-pane', '-p').stdout


def visible_after_prompt(pane, expected=u'$', interval=.1, max=1):
    """Return the visible region once expected is found on last line"""
    t0 = time.time()
    while True:
        if time.time() > t0 + max:
            raise ValueError("prompt %r didn't appear within max time: %r" % (expected, screen))
        screen = visible(pane)
        if screen and screen[-1] == expected:
            return screen
        time.sleep(interval)


def wait_for_prompt(pane, expected=u'$', interval=.01, max=2):
    visible_after_prompt(pane, expected=expected, interval=interval, max=max)


def wait_for_condition(pane, final, query, condition=lambda x, y: x == y,
                       interval=0.01, max=1):
    """Poll for a condition to be true, returning once it is.

    condition takes a response to the query and a final value, returns True if done waiting
    query is a function which returns a value when called on pane
    final is the value we're looking for"""
    t0 = time.time()
    while True:
        if time.time() > t0 + max:
            raise ValueError("contition was never true within max time: cond(%r, %r)" % (last, final))
        last = query(pane)
        if condition(last, final):
            break
        time.sleep(interval)


def cursor_pos(pane):
    """Returns zero-indexed cursor position"""
    process = pane.cmd('list-panes', '-F', '#{pane_height} #{pane_width} #{cursor_x} #{cursor_y}')
    height, width, x, y = [int(x) for x in process.stdout[0].split()]
    return y, x


def width(pane):
    process = pane.cmd('list-panes', '-F', '#{pane_height} #{pane_width} #{cursor_x} #{cursor_y}')
    height, width, x, y = [int(x) for x in process.stdout[0].split()]
    return width


def height(pane):
    process = pane.cmd('list-panes', '-F', '#{pane_height} #{pane_width} #{cursor_x} #{cursor_y}')
    height, width, x, y = [int(x) for x in process.stdout[0].split()]
    return height


wait_for_width = partial(wait_for_condition, query=width)
wait_for_height = partial(wait_for_condition, query=height)


def stepwise_resize_width(pane, final_width):

    initial = width(pane)
    if initial < final_width:
        for _ in range(final_width - initial):
            pane.cmd('resize-pane', '-R', str(1))
    elif initial > final_width:
        for _ in range(initial - final_width):
            pane.cmd('resize-pane', '-L', str(1))
    else:
        return
    wait_for_width(pane, final_width)


def stepwise_resize_height(pane, final_height):

    initial = height(pane)
    if initial < final_height:
        for _ in range(final_height - initial):
            pane.cmd('resize-pane', '-D', str(1))
    elif initial > final_height:
        for _ in range(initial - final_height):
            pane.cmd('resize-pane', '-U', str(1))
    else:
        return
    wait_for_height(pane, final_height)


def window_name(pane):
    """Returns zero-indexed cursor position"""
    process = pane.cmd('list-panes', '-F', '#{window_name}')
    (name, ) = process.stdout[0].split()
    return name


def wait_until_cursor_moves(pane, row, col, interval=.02, max=1):
    """if cursor_row and cursor"""
    t0 = time.time()
    while True:
        if time.time() > t0 + max:
            raise ValueError("cursor row didn't move from initial %r within max time: %r" % ((row, col), visible(pane)))
        if (row, col) != cursor_pos(pane):
            return
        time.sleep(interval)


def send_command(pane, cmd, enter=True, prompt=u'$', maxtime=2):
    if not isinstance(enter, bool):
        raise ValueError("enter should be a bool, got %r" % (enter, ))
    row, col = cursor_pos(pane)
    pane.cmd('send-keys', cmd)
    wait_until_cursor_moves(pane, row, col)
    if enter:
        pane.enter()
    wait_for_prompt(pane, expected=prompt, max=maxtime)


class TmuxPane(object):
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height
        self.tempfiles_to_close = []

    def tmux_config_contents(self):
        return """"""

    def bash_config_contents(self):
        return """export PS1='$'"""

    def tempfile(self, contents, suffix=''):
        tmp = tempfile.NamedTemporaryFile(suffix=suffix)
        self.tempfiles_to_close.append(tmp)
        if py2:
            tmp.write(contents)
        else:
            tmp.write(contents.encode('utf8'))
        tmp.flush()
        return tmp

    def __enter__(self):
        self.tmux_config = self.tempfile(self.tmux_config_contents())
        self.bash_config = self.tempfile(self.bash_config_contents())

        self.server = tmuxp.Server()
        try:
            self.session = self.server.sessions[0]
        except tmuxp.exc.TmuxpException:
            self.session = self.server.new_session()
        self.server.cmd('set', 'automatic-rename', 'on')
        self.server.cmd('set', '-u', 'automatic-rename-format')

        self.window = self.session.new_window(attach=False)
        try:
            self.window.cmd('respawn-pane', '-k', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
            (pane, ) = self.window.panes
            self.window.cmd('respawn-pane', '-k', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
            pane.cmd('split-window', '-h', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
            pane.cmd('split-window', '-v', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
            if self.width is not None:
                pane.set_width(self.width)
            if self.height is not None:
                pane.set_height(self.height)
            wait_for_prompt(pane)
            return pane
        except:
            self.window.kill_window()
            raise

    def __exit__(self, type, value, tb):
        for file in self.tempfiles_to_close:
            file.close()
        self.window.kill_window()

if __name__ == '__main__':
    with TmuxPane(10, 10) as t:
        print(visible(t))
        print(cursor_pos(t))
        t.send_keys('true 1234')
        t.send_keys('true 123456789', False)
        print(visible(t))
        t.set_width(5)
        print('change width to 5')
        print(visible(t))
        print(cursor_pos(t))
        t.send_keys(' ')
        print(visible_after_prompt(t))
        print(visible(t))
        print(cursor_pos(t))
