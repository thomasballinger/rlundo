import tempfile
import time
import tmuxp

def all_contents(pane):
    return pane.tmux('capture-pane', '-epS', '-10000').stdout


def scrollback(pane):
    return pane.tmux('capture-pane', '-epS', '-10000', '-E', '-1').stdout


def visible(pane):
    return pane.tmux('capture-pane', '-ep').stdout


def visible_after_prompt(pane, expected=u'$', interval=.1, max=1):
    """Return the visible region once expected is found on last line"""
    t0 = time.time()
    while True:
        if time.time() > t0 + max:
            raise ValueError("prompt didn't appear within max time: %r" % (screen, ))
        screen = visible(pane)
        if screen and screen[-1] == expected:
            return screen
        time.sleep(interval)


def wait_for_prompt(pane, expected=u'$', interval=.01, max=2):
    visible_after_prompt(pane, expected=expected, interval=interval, max=max)


def cursor_pos(pane):
    """Returns zero-indexed cursor position"""
    process = pane.tmux('list-panes', '-F', '#{pane_height} #{pane_width} #{cursor_x} #{cursor_y}')
    height, width, x, y = [int(x) for x in process.stdout[0].split()]
    return y, x


def window_name(pane):
    """Returns zero-indexed cursor position"""
    process = pane.tmux('list-panes', '-F', '#{window_name}')
    (name, ) = process.stdout[0].split()
    return name


def wait_until_cursor_moves(pane, row, col, interval=.02, max=1):
    """if cursor_row and cursor"""
    t0 = time.time()
    while True:
        if time.time() > t0 + max:
            raise ValueError("cursor row didn't move from initial within max time:")
        if (row, col) != cursor_pos(pane):
            return
        time.sleep(interval)


def send_command(pane, cmd, enter=True, prompt=u'$'):
    row, col = cursor_pos(pane)
    pane.tmux('send-keys', cmd)
    wait_until_cursor_moves(pane, row, col)
    row, _ = cursor_pos(pane)
    pane.enter()
    wait_for_prompt(pane, expected=prompt)


class TmuxPane(object):
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

    def tmux_config_contents(self):
        return """"""

    def bash_config_contents(self):
        return """export PS1='$'
    """

    def __enter__(self):
        self.tmux_config = tempfile.NamedTemporaryFile()
        self.tmux_config.write(self.tmux_config_contents())
        self.tmux_config.flush()
        self.bash_config = tempfile.NamedTemporaryFile()
        self.bash_config.write(self.bash_config_contents())
        self.bash_config.flush()

        #self.server = tmuxp.Server(socket_name='testing',
        #                           config_file=self.tmux_config.name)
        #try:
        #    self.session = self.server.new_session('testing')
        #except tmuxp.exc.TmuxSessionExists:
        #    self.session = self.server.findWhere({"session_name": "testing"})
        self.server = tmuxp.Server()
        self.session = self.server.sessions[0]
        self.server.tmux('set', 'automatic-rename', 'on')
        self.server.tmux('set', '-u', 'automatic-rename-format')

        self.window = self.session.new_window(attach=False)
        self.window.tmux('respawn-pane', '-k', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
        (pane, ) = self.window.panes
        self.window.tmux('respawn-pane', '-k', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
        pane.tmux('split-window', '-h', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
        pane.tmux('split-window', '-v', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
        if self.width is not None:
            pane.set_width(self.width)
        if self.height is not None:
            pane.set_height(self.height)
        wait_for_prompt(pane)
        return pane

    def __exit__(self, type, value, tb):
        self.bash_config.close()
        self.tmux_config.close()
        self.window.kill_window()
        #self.server.kill_server()

if __name__ == '__main__':
    with TmuxPane(10, 10) as t:
        print visible(t)
        print cursor_pos(t)
        t.send_keys('true 1234')
        t.send_keys('true 123456789', False)
        print visible(t)
        t.set_width(5)
        print 'change width to 5'
        print visible(t)
        print cursor_pos(t)
        t.send_keys(' ')
        print visible_after_prompt(t)
        print visible(t)
        print cursor_pos(t)
