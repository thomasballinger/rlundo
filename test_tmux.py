from __future__ import unicode_literals

import unittest
import time

import tmux


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
            self.assertEqual(tmux.cursor_pos(t), (0, 1))
            t.send_keys('true 678')
            self.assertEqual(tmux.cursor_pos(t), (1, 1))
            t.clear()
            tmux.wait_for_prompt(t, '$')
            self.assertEqual(tmux.cursor_pos(t), (0, 1))
            t.send_keys('true 6789')
            self.assertEqual(tmux.cursor_pos(t), (2, 1))

    def test_cursor_position_updated_immediately_after_send_keys(self):
        """No need to wait for prompt etc. """
        with tmux.TmuxPane(10, 10) as t:
            self.assertEqual(tmux.cursor_pos(t), (0, 1))
            t.send_keys('true 678')
            self.assertEqual(tmux.cursor_pos(t), (1, 1))

    def test_resize(self):
        """lines and cursor pos wrap, reported by line

        The front of the current line retains its position!"""
        with tmux.TmuxPane(10, 10) as t:
            self.assertEqual(tmux.cursor_pos(t), (0, 1))
            tmux.send_command(t, 'true 123456789')
            self.assertEqual(tmux.visible(t),
                             ['$true 1234', '56789', '$'])
            self.assertEqual(tmux.cursor_pos(t), (2, 1))
            t.set_width(5)
            self.assertEqual(tmux.cursor_pos(t), (2, 1))
            self.assertEqual(tmux.visible_after_prompt(t),
                             [' 1234', '56789', '$'])
