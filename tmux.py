import tmuxp

from terminal_dsl import split_lines


def all_contents(pane):
    return pane.tmux('capture-pane', '-pS', '-10000').stdout


def scrollback(pane):
    return pane.tmux('capture-pane', '-pS', '-10000', '-E', '-1').stdout


def visible(pane):
    return pane.tmux('capture-pane', '-p').stdout


def rows(pane, width):
    return split_lines(visible(pane), width)


def eval_expr(expr):
    """

    >>> eval_expr("1 + 1")
    [u' python', u' 1 + 1']
    """
    s = tmuxp.Server()
    session = s.new_session('testing')
    window = session.new_window('test')
    (pane, ) = window.panes
    pane.send_keys('python')
    pane.send_keys(expr)
    data = visible(pane)
    s.kill_server()
    return data


class TmuxPane(object):
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

    def __enter__(self):
        self.server = tmuxp.Server()
        try:
            self.session = self.server.new_session('testing')
        except tmuxp.exc.TmuxSessionExists:
            self.session = self.server.findWhere({"session_name": "testing"})

        self.window = self.session.new_window('test')
        (pane, ) = self.window.panes
        if self.width is not None:
            pane.set_width(self.width)
        if self.height is not None:
            pane.set_height(self.height)
        return pane

    def __exit__(self, type, value, tb):
        self.window.kill_window()

if __name__ == '__main__':
    with TmuxPane(10, 10) as t:
        t.send_keys('true 1234')
        t.send_keys('true 123456')
        print rows(t, 10)
        t.set_width(5)
        print rows(t, 5)


