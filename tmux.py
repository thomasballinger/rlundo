import tempfile
import time
import tmuxp

from terminal_dsl import split_lines


def all_contents(pane):
    return pane.tmux('capture-pane', '-epS', '-10000').stdout


def scrollback(pane):
    return pane.tmux('capture-pane', '-epS', '-10000', '-E', '-1').stdout


def visible(pane):
    return pane.tmux('capture-pane', '-ep').stdout


def rows(pane, width):
    return split_lines(visible(pane), width)


def visible_after_prompt(pane, expected=u'$', interval=.1, max=1):
    """Return the visible region once expected is found on last line"""
    t0 = time.time() 
    while True:
        if time.time() > t0 + max:
            raise ValueError("prompt didn't appear within max time: %r" % (screen, ))
        screen = visible(pane)
        if screen[-1] == expected:
            return screen
        time.sleep(interval)


def wait_for_prompt(pane, expected=u'$', interval=.01, max=1):
    visible_after_prompt(pane, expected=expected, interval=interval, max=max)


def cursor_pos(pane):
    """Returns zero-indexed cursor position"""
    process = pane.tmux('list-panes', '-F', '#{pane_height} #{pane_width} #{cursor_x} #{cursor_y}')
    height, width, x, y = [int(x) for x in process.stdout[0].split()]
    return y, x


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

        self.server = tmuxp.Server(socket_name='testing',
                                   config_file=self.tmux_config.name)
        try:
            self.session = self.server.new_session('testing')
        except tmuxp.exc.TmuxSessionExists:
            self.session = self.server.findWhere({"session_name": "testing"})

        self.window = self.session.new_window('test', attach=False)
        self.window.tmux('respawn-pane', '-k', 'bash --rcfile %s --noprofile' % (self.bash_config.name, ))
        (pane, ) = self.window.panes
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
        self.server.kill_server()

if __name__ == '__main__':
    with TmuxPane(10, 10) as t:
        print visible(t)
        print cursor_pos(t)
        t.send_keys('true 1234')
        t.send_keys('true 123456789', False)
        t.set_width(5)
        print cursor_pos(t)
        t.send_keys(' ')
        print visible_after_prompt(t)
        print cursor_pos(t)
