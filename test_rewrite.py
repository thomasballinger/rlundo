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
            t.send_keys('python rewrite.py')
            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$ python rewrite.py', '>'])

            self.assertEqual(tmux.cursor_pos(t), (1, 1))
            tmux.wait_for_prompt(t, '>')

            save()
            t.tmux('send-keys', 'hello!')
            t.enter()
            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$ python rewrite.py', '>hello!', '>'])
            restore(t)
            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$ python rewrite.py', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))
