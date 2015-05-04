#!/usr/bin/env python

"""
test_rlundo
----------------------------------

Integration test for undo features implemented in rlundo. It sends commands
to an open tmux terminal using 'undo' and checks that the output is the
expected one.

To create new tests you may one to use py_logger to capture decoded bytes from
a python terminal and see how they look:
    `python py_logger.py ipython` or
    `python py_logger.py python`

For some reason, the formatting is not handled properly by tmux.visible()
method and thus the decode logging captured may differ, it has to be used only
as a guide.
"""

from __future__ import unicode_literals
import unittest
import nose
import sys

import tmux


class ActualUndo(tmux.TmuxPane):

    """
    Run a tmux pane instance to start a repl, send commands, use undo and check
    the expected output.

    ActualUndo is better used within the context manager and tmux module can be
    used to send commands:

        with ActualUndo(80, 30) as t:
            tmux.send_command(t, "print 'hi'", prompt=expected_prompt)
            output = tmux.visible(t)

    If you want to see what's going on while sending commands from a repl, you
    can do that by oppening a session with the __enter__() method and
    attaching a tmux session to it.

        (in ipython)
        from test_rlundo import ActualUndo
        w = ActualUndo(50, 30).__enter__()

        (in another terminal)
        tmux attach

        (in ipython)
        w.send_keys("a = 1")
        w.send_keys("a")

        In the other terminal you will see the session inputs and outputs.
    """

    def bash_config_contents(self):
        python_env = sys.executable
        return """
        export PS1='$'
        alias irb="python rlundo.py /usr/bin/irb"
        alias ipy="{} rlundo.py ipython"
        """.format(python_env)

    def __enter__(self):
        """Initialize a pane with an undo scenario.

        undo schenarios always start by calling python rewrite.py

        >>> with ActualUndo(30, 10) as t:
        ...     tmux.send_command(t, 'echo hello')
        ...     print(tmux.visible_after_prompt(t, expected=u'$'))
        [u'$echo hello', u'hello', u'$']
        """
        return tmux.TmuxPane.__enter__(self)


class IPyPrompt(object):

    @classmethod
    def in_formatted(cls, num):
        """Build ipython "In" prompt with formatting.

        For some reason tmux doesn't deal with formatting in the same way that
        normal ipython does, the proper ipython line for prompt is included as
        a comment below."""
        # return u'\x1b[34mIn [\x1b[1m{}\x1b[0;34m]:'.format(num)
        return u'\x1b[34mIn [\x1b[1m{}\x1b[0m]:'.format(num)

    @classmethod
    def out_formatted(cls, num):
        """Build ipython "Out" prompt with formatting.

        For some reason tmux doesn't deal with formatting in the same way that
        normal ipython does, the proper ipython line for prompt is included as
        a comment below."""
        # return u'\x1b[31mOut[\x1b[1m{}\x1b[0;34m]:'.format(num)
        return u'\x1b[31mOut[\x1b[1m{}\x1b[0m]:'.format(num)

    @classmethod
    def new_l_formatted(cls):
        """Build ipython new line in the same "In" prompt with formatting.

        For some reason tmux doesn't deal with formatting in the same way that
        normal ipython does, the proper ipython line for prompt is included as
        a comment below."""
        # return u'\x1b[34m   ...: \x1b[0m'
        return u'\x1b[34m   ...: \x1b[39m'

    @classmethod
    def in_prompt(cls, num):
        """Build ipython "In" prompt without formatting."""
        return u'In [{}]:'.format(num)

    @classmethod
    def out_prompt(cls, num):
        """Build ipython "Out" prompt without formatting."""
        return u'Out[{}]:'.format(num)

    @classmethod
    def new_l_prompt(cls):
        """Build ipython new line inside an "In" prompt without formatting."""
        return u'   ...:'


class TestUndoableIpythonWithTmux(unittest.TestCase):

    """Use ActualUndo and tmux to send commands to an IPython repl and check
    undo feature rewrite the terminal as expected.
    """

    # @unittest.skip("skip")
    def test_simple(self):
        """Test sending commands and reading formatted output with tmux."""
        with ActualUndo(80, 30) as t:
            tmux.send_command(t, 'ipy', prompt=IPyPrompt.in_formatted(1))
            tmux.send_command(t, 'a = 1', prompt=IPyPrompt.in_formatted(2))
            tmux.send_command(t, 'a', prompt=IPyPrompt.in_formatted(3))
            tmux.send_command(t, 'def foo():',
                              prompt=IPyPrompt.new_l_formatted())
            tmux.send_command(t, 'print "hi"',
                              prompt=IPyPrompt.new_l_formatted())
            tmux.send_command(t, ' ', prompt=IPyPrompt.in_formatted(4))
            output = tmux.visible(t)
            lines = [IPyPrompt.in_formatted(1) + ' \x1b[39ma = 1',
                     IPyPrompt.in_formatted(2) + ' \x1b[39ma',
                     IPyPrompt.out_formatted(2) + ' \x1b[39m1',
                     IPyPrompt.in_formatted(3) + ' \x1b[39mdef foo():',
                     IPyPrompt.new_l_formatted() + '    print "hi"',
                     IPyPrompt.new_l_formatted() + '',
                     IPyPrompt.in_formatted(4)]
            self.assertEqual(output[-7:], lines)

    # @unittest.skip("skip")
    def test_undo_simple(self):
        """Test undoing one liner command in ipython."""
        with ActualUndo(80, 30) as t:

            # type some commands
            tmux.send_command(t, 'ipy', prompt=IPyPrompt.in_formatted(1))
            tmux.send_command(t, 'a = 1', prompt=IPyPrompt.in_formatted(2))
            tmux.send_command(t, 'a', prompt=IPyPrompt.in_formatted(3))
            output = tmux.visible_without_formatting(t)
            lines = [IPyPrompt.in_prompt(1) + ' a = 1',
                     IPyPrompt.in_prompt(2) + ' a',
                     IPyPrompt.out_prompt(2) + ' 1',
                     IPyPrompt.in_prompt(3)]
            self.assertEqual(output[-4:], lines)

            # undo
            tmux.send_command(t, 'undo', prompt=IPyPrompt.in_formatted(2))
            output = tmux.visible_without_formatting(t)
            self.assertEqual(output[-2:],
                             lines[:1] + [IPyPrompt.in_prompt(2)])

    # @unittest.skip("skip")
    def test_undo_multiple_input_lines(self):
        """Test udoing a line of a multiple lines command in ipython."""
        with ActualUndo(80, 30) as t:

            # type some commands
            tmux.send_command(t, 'ipy', prompt=IPyPrompt.in_formatted(1))
            tmux.send_command(t, 'def foo():',
                              prompt=IPyPrompt.new_l_formatted())
            tmux.send_command(t, 'print "hi"',
                              prompt=IPyPrompt.new_l_formatted())
            tmux.send_command(t, ' ', prompt=IPyPrompt.in_formatted(2))
            tmux.send_command(t, 'foo()', prompt=IPyPrompt.in_formatted(3))
            output = tmux.visible_without_formatting(t)
            lines = [IPyPrompt.in_prompt(1) + ' def foo():',
                     IPyPrompt.new_l_prompt() + '     print "hi"',
                     IPyPrompt.new_l_prompt() + '',
                     IPyPrompt.in_prompt(2) + ' foo()',
                     'hi',
                     IPyPrompt.in_prompt(3)]
            self.assertEqual(output[-6:], lines)

            # undo
            tmux.send_command(t, 'undo', prompt=IPyPrompt.in_formatted(2))
            output = tmux.visible_without_formatting(t)
            self.assertEqual(output[-4:], lines[:3] + [IPyPrompt.in_prompt(2)])

            # undo again
            tmux.send_command(t, 'undo', prompt=IPyPrompt.new_l_formatted())
            output = tmux.visible_without_formatting(t)
            self.assertEqual(output[-3:], lines[:2] + [IPyPrompt.new_l_prompt()])


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
    # unittest.main()
