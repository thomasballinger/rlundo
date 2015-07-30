from __future__ import unicode_literals

import unittest

from . import tmux
from . import terminal_dsl


class TestTmuxPaneInfo(unittest.TestCase):
    def test_contents(self):
        with tmux.TmuxPane(20, 5) as t:
            tmux.send_command(t, 'echo 01234567890123456789')
            tmux.send_command(t, 'echo 01234567890123456789')
            self.assertEqual(tmux.all_contents(t),
                             ['$echo 01234567890123',
                              '456789',
                              '01234567890123456789',
                              '$echo 01234567890123',
                              '456789',
                              '01234567890123456789',
                              '$'])
            self.assertEqual(tmux.all_lines(t),
                             ['$echo 01234567890123'
                              '456789',
                              '01234567890123456789',
                              '$echo 01234567890123'
                              '456789',
                              '01234567890123456789',
                              '$'])


class TestTerminalDSL(unittest.TestCase):
    def test_simple(self):
        with tmux.TmuxPane(10, 10) as t:
            tmux.send_command(t, 'true 1')
            self.assertEqual(tmux.visible(t), ['$true 1',
                                               '$'])
            tmux.send_command(t, 'true 2')
            termstate = terminal_dsl.TerminalState.from_tmux_pane(t)
            expected = terminal_dsl.TerminalState(
                lines=['$true 1', '$true 2', '$'],
                cursor_line=2, cursor_offset=1, width=10, height=10,
                history_height=0)
        self.assertEqual(expected, termstate, expected.visible_diff(termstate))

    def test_wrapped_lines(self):
        with tmux.TmuxPane(10, 10) as t:
            tmux.send_command(t, 'true 12345')
            self.assertEqual(tmux.visible(t), ['$true 1234',
                                               '5',
                                               '$'])
            tmux.send_command(t, 'true 1234')
            termstate = terminal_dsl.TerminalState.from_tmux_pane(t)
            expected = terminal_dsl.TerminalState(
                lines=['$true 12345', '$true 1234', '$'],
                cursor_line=2, cursor_offset=1, width=10, height=10,
                history_height=0)
        self.assertEqual(expected, termstate, expected.visible_diff(termstate))


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
            self.assertEqual(tmux.scrollback(t), [])
            t.send_keys('true 2')
            self.assertEqual(tmux.visible(t), ['$ true 1',
                                               '$ true 2',
                                               '$'])
            self.assertEqual(tmux.scrollback(t), [])

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
            tmux.stepwise_resize_width(t, 20)
            tmux.stepwise_resize_height(t, 20)

    def test_initial_size(self):
        tmux.assert_terminal_wide_enough(70)
        with tmux.TmuxPane(70, 3) as t:
            self.assertEqual(tmux.width(t), 70)
            self.assertEqual(tmux.height(t), 3)
