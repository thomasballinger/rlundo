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


class TestTmux(unittest.TestCase):
    def test_simple(self):
        with tmux.TmuxPane(10, 10) as t:
            t.send_keys('true 1')
            self.assertEqual(tmux.visible(t), [u'$ true 1',
                                               u'$'])
            t.send_keys('true 2')
            self.assertEqual(tmux.visible(t), [u'$ true 1',
                                               u'$ true 2',
                                               u'$'])

    def test_resize(self):
        """lines and cursor pos wrap, reported by line

        send_keys( , False) sends an extra space
        trailing whitespace is annoyingly ignored"""
        with tmux.TmuxPane(10, 10) as t:
            self.assertEqual(tmux.cursor_pos(t), (0, 1))
            t.send_keys('true 1234')
            t.send_keys('true 123456789', False)
            t.set_width(5)
            self.assertEqual(tmux.cursor_pos(t), (1, 16))
            t.send_keys('')
            self.assertEqual(tmux.visible_after_prompt(t),
                             [u'$ true 1234', u'$ true 123456789', u'$'])


class TestRunWithTmux(unittest.TestCase):

    def test_running_rewrite(self):
        with tmux.TmuxPane(10, 10) as t:
            t.send_keys('python rewrite.py')
            self.assertEqual(tmux.visible_after_prompt(t, u'>'),
                             [u'$ python rewrite.py', u'>'])

    def test_simple_save_and_restore(self):
        with tmux.TmuxPane(40, 40) as t:
            t.send_keys('python rewrite.py')
            self.assertEqual(tmux.visible_after_prompt(t, u'>'),
                             [u'$ python rewrite.py', u'>'])

            self.assertEqual(tmux.cursor_pos(t), (1, 1))
            tmux.wait_for_prompt(t, u'>')

            save()
            t.tmux('send-keys', 'hello!')
            t.enter()
            self.assertEqual(tmux.visible_after_prompt(t, u'>'),
                             [u'$ python rewrite.py', u'>hello!', u'>'])
            restore(t)
            self.assertEqual(tmux.visible_after_prompt(t, u'>'),
                             [u'$ python rewrite.py', u'>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))
