from __future__ import unicode_literals

import re
import socket
import textwrap
import time
import unittest

import terminal_dsl
import tmux
import rewrite


def save():
    s = socket.socket()
    s.connect(('localhost', 4242))
    assert '' == s.recv(100)


def restore(t):
    """Pretend to be the program we're undoing and print prompt"""
    s = socket.socket()
    s.connect(('localhost', 4243))
    assert '' == s.recv(100)
    t.tmux('send-keys', '>')
    time.sleep(.1)


class TestRewriteHelpers(unittest.TestCase):
    def test_history(self):
        self.assertEqual(rewrite.history(['>>> print "hello\\n"*3\nhello\nhello\nhello\n'
                                          '>>> 1 + 1\n2\n',
                                          '>>> ']),
                         ['>>> print "hello\\n"*3',
                          'hello',
                          'hello',
                          'hello',
                          '>>> 1 + 1',
                          '2',
                          '>>> '])


class TestRunWithTmux(unittest.TestCase):

    def test_cursor_query(self):
        with tmux.TmuxPane(40, 10) as t:
            tmux.send_command(t, 'true 1234')
            tmux.send_command(t, 'true 1234')
            program = "import findcursor, sys; print(findcursor.get_cursor_position(sys.stdout, sys.stdin))"
            tmux.send_command(t, 'python -c "%s"' % (program, ))
            lines = tmux.visible(t)
            while lines[-1] == u'$':
                lines.pop()
            line = lines[-1]
            self.assertTrue(len(line) > 1, repr(line))
            row, col = [int(x) for x in re.search(
                r'[(](\d+), (\d+)[)]', line).groups()]
            self.assertEqual(tmux.cursor_pos(t), (row+1, col+1))

    def test_running_rewrite(self):
        with tmux.TmuxPane(40, 10) as t:
            t.send_keys('python rewrite.py')
            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$ python rewrite.py', '>'])

    def test_simple_save_and_restore(self):
        with tmux.TmuxPane(40, 10) as t:
            tmux.send_command(t, 'python rewrite.py', prompt=u'>')
            self.assertEqual(tmux.visible(t), ['$python rewrite.py', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))
            save()

            tmux.send_command(t, 'hello!', prompt=u'>')
            self.assertEqual(tmux.visible(t),
                             ['$python rewrite.py', '>hello!', '>'])
            restore(t)

            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$python rewrite.py', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))

    def test_scroll_down(self):
        with tmux.TmuxPane(40, 8) as t:
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'python rewrite.py', prompt=u'>')
            self.assertEqual(tmux.visible(t),
                             (['$true']*5 +
                              ['$python rewrite.py',
                               '>']))
            self.assertEqual(tmux.cursor_pos(t), (6, 1))
            save()
            tmux.send_command(t, 'hello!', prompt=u'>')
            save()

            tmux.send_command(t, 'hi again!', prompt=u'>')
            save()
            self.assertEqual(tmux.visible(t),
                             ['$true']*4 + ['$python rewrite.py',
                                            '>hello!',
                                            '>hi again!',
                                            '>'])
            restore(t)

            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$true']*4 + ['$python rewrite.py',
                                            '>hello!',
                                            '>'])
            self.assertEqual(tmux.cursor_pos(t), (6, 1))

    def test_scroll_off(self):
        """Scroll down causing recorded output to scroll off the top."""
        with tmux.TmuxPane(40, 3) as t:
            tmux.send_command(t, 'python rewrite.py', prompt=u'>')
            save()
            self.assertEqual(tmux.visible(t), ['$python rewrite.py', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))

            tmux.send_command(t, 'hello!', prompt=u'>')
            save()

            tmux.send_command(t, 'hi again!', prompt=u'>')
            save()
            self.assertEqual(tmux.visible(t),
                             ['>hello!', '>hi again!', '>'])
            restore(t)
            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['>hello!', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))

    def test_rewind_to_scrolled_off_prompt(self):
        """Recreating history in visible area because undo goes offscreen

        For this we need to track history, do math to place
        this history in the visible window, and track scrolling
        or cursor position to know that we've run out of space.
        I think we don't need an emulator yet - just cursor querying should do.
        """
        with tmux.TmuxPane(60, 3) as t:
            tmux.send_command(t, 'python rewrite.py', prompt=u'>')
            save()
            self.assertEqual(tmux.visible(t), ['$python rewrite.py', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))

            tmux.send_command(t, 'hi there!', prompt=u'>')
            save()

            tmux.send_command(t, 'hello!', prompt=u'>')
            tmux.send_command(t, 'hi again!', prompt=u'>')
            tmux.send_command(t, 'hey!', prompt=u'>')
            save()
            self.assertEqual(tmux.scrollback(t),
                             ['$python rewrite.py',
                              '>hi there!',
                              '>hello!'])
            self.assertEqual(tmux.visible(t),
                             ['>hi again!',
                              '>hey!',
                              '>'])
            restore(t)
            self.assertEqual(tmux.scrollback(t),
                             ['$python rewrite.py',
                              '>hi there!',
                              '>hello!',
                              '#<---History contiguity broken by rewind--->'])
            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['>hi there!',
                              '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))


class UndoScenario(tmux.TmuxPane):
    def bash_config_contents(self):
        return """
        export PS1='$'
        alias rw="python rewrite.py python %s"
        """ % (self.python_script.name, )

    def python_script_contents(self):
        return textwrap.dedent("""\
        raw_input(">")
        while True:
            raw_input()
        """)

    def __init__(self, termstate):
        self.validate_termstate(termstate)
        self.termstate = termstate
        tmux.TmuxPane.__init__(self, termstate.width, termstate.height)

    @classmethod
    def validate_termstate(cls, termstate):
        """Check that termstate represents a valid undo scenario

        Undo scenarios must start with "$rw" and then consist
        of pairs of > prompts with commands followed by zero
        or more lines of output.

        >>> termstate = terminal_dsl.TerminalState(
        ...     ['>a', 'b', 'c', '>d', 'e', '>'], cursor_line=5,
        ...     cursor_offset=1, width=10, height=10, history_height=0)
        >>> validate_termstate(termstate)
        Traceback (most recent call last):
            ...
        ValueError: termstate doesn't start with a call to rw
        """
        if not termstate.lines[0] == '$rw':
            raise ValueError("termstate doesn't start with a call to rw")

    def check_port(self, port):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', port))
        s.close()

    def __enter__(self):
        """Initialize a pane with an undo scenario.

        undo schenarios always start by calling python rewrite.py

        >>> termstate = terminal_dsl.TerminalState(
        ...     ['$rw', '>a', 'b', 'c', '>d', 'e', '>'], cursor_line=5,
        ...     cursor_offset=1, width=10, height=10, history_height=0)
        >>> with UndoScenario(termstate) as t:
        ...     print tmux.visible_after_prompt(t, expected=u'>')
        ['$rw', '>a', 'b', 'c', '>d', 'e', '>']
        """
        self.check_port(4242)
        self.check_port(4243)
        self.python_script = self.tempfile(self.python_script_contents())
        pane = tmux.TmuxPane.__enter__(self)

        lines = self.termstate.lines[:]
        assert lines.pop(0) == '$rw'
        tmux.send_command(pane, 'rw', prompt=u'>')
        save()
        first_line = lines.pop(0)
        assert first_line.startswith('>')
        pane.tmux('send-keys', first_line[1:])
        pane.enter()
        tmux.wait_until_cursor_moves(pane, 1, 1)
        for i, line in enumerate(lines):
            if i == self.termstate.cursor_line:
                assert len(lines) == i - 1
                pane.tmux('send-keys', line)
            elif line.startswith('>'):
                tmux.send_command(pane, '>', enter=False, prompt=u'>')
                save()
                pane.tmux('send-keys', line[1:])
                pane.enter()
            else:
                row, col = tmux.cursor_pos(pane)
                pane.tmux('send-keys', line)
                pane.enter()
                tmux.wait_until_cursor_moves(pane, row, col)

        return pane


class TestUndoScenario(unittest.TestCase):
    def test_initial(self):
        lines = ['$rw', '>a', 'b', 'c', '>d', 'e', '>']
        termstate = terminal_dsl.TerminalState(
            lines, cursor_line=6, cursor_offset=1,
            width=10, height=10, history_height=0)
        with UndoScenario(termstate) as t:
            output = tmux.visible(t)
            print output
            print tmux.all_contents(t)
            self.assertEqual(output, lines)
