from __future__ import unicode_literals

import re
import socket
import time
import unittest

import tmux


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
            time.sleep(1)
            self.assertEqual(tmux.scrollback(t),
                             ['$python rewrite.py',
                              '>hi there!',
                              '>hello!'])
            self.assertEqual(tmux.visible(t),
                             ['>hi again!',
                              '>hey!',
                              '>'])
            restore(t)
            time.sleep(1)
            self.assertEqual(tmux.scrollback(t),
                             ['$python rewrite.py',
                              '>hi there!',
                              '>hello!',
                              '#<---History contiguity broken by rewind--->'])
            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['>hi there!',
                              '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))
