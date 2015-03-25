from __future__ import unicode_literals

import socket
import unittest
import time

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
    time.sleep(.5)
    t.tmux('send-keys', '>')


class TestRunWithTmux(unittest.TestCase):

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
            self.assertEqual(tmux.visible(t), ['$true']*5 + ['$python rewrite.py', '>'])
            self.assertEqual(tmux.cursor_pos(t), (6, 1))
            save()
            tmux.send_command(t, 'hello!', prompt=u'>')
            save()

            tmux.send_command(t, 'hi again!', prompt=u'>')
            save()
            self.assertEqual(tmux.visible(t),
                             ['$true']*4 + ['$python rewrite.py', '>hello!', '>hi again!', '>'])
            restore(t)

            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$true']*4 + ['$python rewrite.py', '>hello!', '>'])
            self.assertEqual(tmux.cursor_pos(t), (6, 1))

    def test_scroll_off(self):
        with tmux.TmuxPane(40, 3) as t:
            tmux.send_command(t, 'python rewrite.py', prompt=u'>')
            self.assertEqual(tmux.visible(t), ['$python rewrite.py', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))
            tmux.send_command(t, 'hello!', prompt=u'>')
            save()

            tmux.send_command(t, 'hi again!', prompt=u'>')
            self.assertEqual(tmux.visible(t),
                             ['>hello!', '>hi again!', '>'])
            restore(t)

            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['>hi again!', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))
