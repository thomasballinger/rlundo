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


class TestTmux(unittest.TestCase):
    def test_send_command(self):
        with tmux.TmuxPane(20, 20) as t:
            tmux.send_command(t, 'sleep .1; echo hi')
            self.assertEqual(tmux.visible(t), ['$sleep .1; echo hi',
                                               'hi',
                                               '$'])

    def test_simple(self):
        with tmux.TmuxPane(10, 10) as t:
            t.send_keys('true 1')
            self.assertEqual(tmux.visible(t), ['$ true 1',
                                               '$'])
            t.send_keys('true 2')
            self.assertEqual(tmux.visible(t), ['$ true 1',
                                               '$ true 2',
                                               '$'])

    def test_lines_wrap(self):
        """lines and cursor position wrap

        This is the reason we're using tmux and not vt100 emulator"""
        with tmux.TmuxPane(10, 10) as t:
            pass

#    def test_resize(self):
#        """lines and cursor pos wrap, reported by line
#
#        resizes happen immediately
#        resizes never move the cursor down
#        trailing whitespace is annoyingly ignored
#        send_keys calls don't block
#        """
#        with tmux.TmuxPane(10, 10) as t:
#            self.assertEqual(tmux.cursor_pos(t), (0, 1))
#            t.send_keys('true 1234')
#            t.send_keys('true 123456789')
#            time.sleep(1)
#            self.assertEqual(tmux.cursor_pos(t), (4, 1))
#            t.set_width(5)
#            self.assertEqual(tmux.cursor_pos(t), (4, 1))
#            t.send_keys('')
#            self.assertEqual(tmux.visible_after_prompt(t),
#                             ['$ tru', 'e 123', '4', '$ tru', 'e 123', '45678', '9', '$'])
#
#            print tmux.visible(t)
#            self.fail()



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
