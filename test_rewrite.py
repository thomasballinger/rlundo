from __future__ import unicode_literals

import ast
import os
import re
import socket
import time
import unittest

import nose

import terminal_dsl
import tmux
import rewrite
import scenarioscript


def save():
    s = socket.socket(family=socket.AF_UNIX)
    s.connect(os.environ['RLUNDO_SAVE'])
    assert b'' == s.recv(100)


def restore(t):
    """Pretend to be the program we're undoing and print prompt"""
    s = socket.socket(family=socket.AF_UNIX)
    s.connect(os.environ['RLUNDO_RESTORE'])
    assert b'' == s.recv(100)
    t.cmd('send-keys', '>')
    time.sleep(.1)


class DiagramsWithTmux(object):
    maxDiff = 10000

    def assert_undo(self, diagram, slow=False):
        states = [terminal_dsl.parse_term_state(x)[1]
                  for x in terminal_dsl.divide_term_states(diagram)]
        if len(states) < 2:
            raise ValueError("Diagram has only one state")
        with UndoScenario(states[0]) as t:
            UndoScenario.initialize(t, states[0])
            if slow: time.sleep(1)
            for before, after in zip(states[:-1], states[1:]):
                self.resize(before, after, t)
                if slow: time.sleep(1)
                if self.should_undo(before, after):
                    restore(t)
                    if slow: time.sleep(1)
                actual = terminal_dsl.TerminalState.from_tmux_pane(t)
                self.assertEqual(after, actual, after.visible_diff(actual))
                self.assertEqual(tmux.all_contents(t),
                                 rewrite.linesplit(after.lines, after.width))

    def resize(self, before, after, t):
        tmux.stepwise_resize_width(t, after.width)
        tmux.stepwise_resize_height(t, after.height)

    def should_undo(self, s1, s2):
        return (len(s1.lines) > len(s2.lines) or
                s1.lines.count('>undo') > s2.lines.count('>undo'))


class TestDiagramsWithTmux(unittest.TestCase, DiagramsWithTmux):
    def test_simple_undo(self):
        self.assert_undo('''
            before             after
        +-----------+      +-----------+
        |$rw        |      |$rw        |
        |>1 + 1     |      |>1 + 1     |
        |usually 2  |      |usually 2  |
        +-----------+      +-----------+
        |>2 + 2     |      |>2 + 2     |
        |notquite 4 |      |notquite 4 |
        |>3         |      |>@         |
        |3          |      ~           ~
        |>@         |      ~           ~
        ~           ~      ~           ~
        +-----------+      +-----------+
        ''')

    def test_resizing_window(self):
        lines = [u'$rw',
                 u'>1 + 1',
                 u'usually 2',
                 u'>2 + 2',
                 u'notquite 4',
                 u'>3',
                 u'3',
                 u'>']
        termstate = terminal_dsl.TerminalState(
            lines=lines, cursor_line=7, cursor_offset=1, width=11,
            height=6, history_height=3)
        with UndoScenario(termstate) as t:
            UndoScenario.initialize(t, termstate)
            tmux.stepwise_resize_width(t, 11)
            self.assertEqual(tmux.all_contents(t), lines)

    def test_simple_resize(self):
        self.assert_undo('''
            before              after
        +-----------+      +--------------+
        |$rw        |      |$rw           |
        |>1 + 1     |      |>1 + 1        |
        |usually 2  |      |usually 2     |
        +-----------+      +--------------+
        |>2 + 2     |      |>2 + 2        |
        |notquite 4 |      |notquite 4    |
        |>3         |      |>3            |
        |3          |      |3             |
        |>@         |      |>@            |
        ~           ~      ~              ~
        +-----------+      +--------------+
        ''')

    def test_multistep(self):
        self.assert_undo('''
           initial            widen             narrow        widen and undo
        +-----------+    +--------------+    +----------+    +--------------+
        |$rw        |    |$rw           |    |$rw       |    |$rw           |
        |>1 + 1     |    |>1 + 1        |    |>1 + 1    |    |>1 + 1        |
        |usually 2  |    |usually 2     |    |usually 2 |    |usually 2     |
        +-----------+    +--------------+    +----------+    +--------------+
        |>2 + 2     |    |>2 + 2        |    |>2 + 2    |    |>2 + 2        |
        |notquite 4 |    |notquite 4    |    |notquite 4|    |notquite 4    |
        |>3         |    |>3            |    |>3        |    |>@            |
        |3          |    |3             |    |3         |    ~              ~
        |>@         |    |>@            |    |>@        |    ~              ~
        ~           ~    ~              ~    ~          ~    ~              ~
        +-----------+    +--------------+    +----------+    +--------------+
        ''')


class TestRewriteHelpers(unittest.TestCase):
    def test_history(self):
        self.assertEqual(rewrite.history(
                         ['>>> print("hello\\n"*3)\nhello\nhello\nhello\n',
                          '>>> 1 + 1\n2\n',
                          '>>> ']),
                         ['>>> print("hello\\n"*3)',
                          'hello',
                          'hello',
                          'hello',
                          '>>> 1 + 1',
                          '2',
                          '>>> '])

    def test_count_lines(self):
        self.assertEqual(rewrite.count_lines(b"1234\n123456", 4), 2)
        self.assertEqual(rewrite.count_lines(b"1234\n123456", 10), 1)
        self.assertEqual(rewrite.count_lines(b"> undo\r\n> 1\r\n1\r\n", 10), 3)
        self.assertEqual(rewrite.count_lines(b"\x01\x1b[0;32m\x02In [\x01\x1b[1;32m\x021\x01\x1b[0;32m\x02]: 1\n\x01\x1b[0m\x02\x1b[0;31mOut[\x1b[1;31m1\x1b[0;31m]: \x1b[0m1\n\n", 40), 3)
        self.assertEqual(rewrite.count_lines(b'\r\n\x1b[0;32mIn [\x1b[1;32m2\x1b[0;32m]: \x1b[0mundo\x1b[0;32m   ...: \x1b[0m     \r\n\r\n', 40), 3)

        with open("input_with_colours.txt", "r") as f:
            data = ast.literal_eval('b"""'+f.read()+'"""')
        self.assertEqual(rewrite.count_lines(data, 80), 6)

    def test_linesplit(self):
        self.assertEqual(rewrite.linesplit(["1234", "123456"], 4),
                         ["1234", "1234", "56"])
        self.assertEqual(rewrite.linesplit(["1234", "123456"], 10),
                         ["1234", "123456"])

    def test_visible_characters(self):
        self.assertEqual(rewrite._visible_characters("1234"), 4)
        self.assertEqual(rewrite._visible_characters("1234\n"), 4)
        self.assertEqual(rewrite._visible_characters("\x1b[0;32m1234"), 4)
        self.assertEqual(rewrite._visible_characters("\x1b[0m1234"), 4)

    def test_rows_required(self):
        self.assertEqual(rewrite._rows_required("1234", 4), 1)
        self.assertEqual(rewrite._rows_required("1234", 3), 2)
        self.assertEqual(rewrite._rows_required("1234", 2), 2)
        self.assertEqual(rewrite._rows_required("1234", 1), 4)
        self.assertEqual(rewrite._rows_required("\x1b[0;32m1234", 2), 2)


class TmuxPaneWithAddrsInEnv(tmux.TmuxPane):
    def bash_config_contents(self):
        self.save_addr = rewrite.temp_name('save')
        self.restore_addr = rewrite.temp_name('restore')
        os.environ['RLUNDO_SAVE'] = self.save_addr
        os.environ['RLUNDO_RESTORE'] = self.restore_addr
        return """
        export PS1='$'
        export SAVE={}
        export RESTORE={}
        """.format(self.save_addr, self.restore_addr)


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
            self.assertEqual(tmux.visible_after_prompt(t, '>', max=4),
                             ['$ python rewrite.py', '>'])

    def test_simple_save_and_restore(self):
        with TmuxPaneWithAddrsInEnv(80, 10) as t:
            tmux.send_command(t, 'python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', prompt=u'>')
            self.assertEqual(tmux.visible(t), ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))
            save()

            tmux.send_command(t, 'hello!', prompt=u'>')
            self.assertEqual(tmux.visible(t),
                             ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', '>hello!', '>'])
            restore(t)

            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))

    def test_scroll_down(self):
        with TmuxPaneWithAddrsInEnv(70, 8) as t:
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'true')
            tmux.send_command(t, 'python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', prompt=u'>')
            self.assertEqual(tmux.visible(t),
                             (['$true']*5 +
                              ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE',
                               '>']))
            self.assertEqual(tmux.cursor_pos(t), (6, 1))
            save()
            tmux.send_command(t, 'hello!', prompt=u'>')
            save()

            tmux.send_command(t, 'hi again!', prompt=u'>')
            save()
            self.assertEqual(tmux.visible(t),
                             ['$true']*4 + ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE',
                                            '>hello!',
                                            '>hi again!',
                                            '>'])
            restore(t)

            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['$true']*4 + ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE',
                                            '>hello!',
                                            '>'])
            self.assertEqual(tmux.cursor_pos(t), (6, 1))

    def test_scroll_off(self):
        """Scroll down causing recorded output to scroll off the top."""
        with TmuxPaneWithAddrsInEnv(60, 3) as t:
            tmux.send_command(t, 'python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', prompt=u'>')
            save()
            self.assertEqual(tmux.visible(t), ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', '>'])
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
        with TmuxPaneWithAddrsInEnv(60, 3) as t:
            tmux.send_command(t, 'python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', prompt=u'>')
            save()
            self.assertEqual(tmux.visible(t), ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE', '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))

            tmux.send_command(t, 'hi there!', prompt=u'>')
            save()

            tmux.send_command(t, 'hello!', prompt=u'>')
            tmux.send_command(t, 'hi again!', prompt=u'>')
            tmux.send_command(t, 'hey!', prompt=u'>')
            save()
            self.assertEqual(tmux.scrollback(t),
                             ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE',
                              '>hi there!',
                              '>hello!'])
            self.assertEqual(tmux.visible(t),
                             ['>hi again!',
                              '>hey!',
                              '>'])
            restore(t)
            self.assertEqual(tmux.scrollback(t),
                             ['$python rewrite.py --save-addr $SAVE --restore-addr $RESTORE',
                              '>hi there!',
                              '>hello!',
                              '#<---History contiguity broken by rewind--->'])
            self.assertEqual(tmux.visible_after_prompt(t, '>'),
                             ['>hi there!',
                              '>'])
            self.assertEqual(tmux.cursor_pos(t), (1, 1))


class TestWrappedLines(unittest.TestCase, DiagramsWithTmux):
    maxDiff = 10000

    def test_wrapped_undo(self):
        self.assert_undo("""
        +------+   +------+
        +------+   +------+
        |$rw   |   |$rw   |
        |>1    |   |>1    |
        |>stuff|   |>@    |
        |abcdef+   ~      ~
        |ghijk |   ~      ~
        |>@    |   ~      ~
        ~      ~   ~      ~
        +------+   +------+
        """)

    def test_wrapped_undo_after_narrow(self):
        self.assert_undo("""
                                 +------+  +------+
        +------+  +-----------+  |$rw   |  |$rw   |
        +------+  +-----------+  +------+  +------+
        |$rw   |  |$rw        |  |>1    |  |>1    |
        |>1    |  |>1         |  |>stuff|  |>@    |
        |>stuff|  |>stuff     |  |abcdef+  ~      ~
        |abcdef+  |abcdefghijk+  |ghijkl+  ~      ~
        |ghijkl+  |lmnopq     |  |mnopq |  ~      ~
        |mnopq |  |>@         |  |>@    |  ~      ~
        |>@    ~  ~           ~  ~      ~  ~      ~
        +------+  +-----------+  +------+  +------+
        """)

    def test_irb_style_undo(self):
        self.assert_undo("""
        +----------+     +----------+
        +----------+     +----------+
        |$rw       |     |$rw       |
        |>1 + 1    |     |>@        |
        |2         |     ~          ~
        |>undo     |     ~          ~
        |@         |     ~          ~
        +----------+     +----------+
        """)

    def test_undo_back_into_history(self):
        self.assert_undo("""
                         +----------+
        +----------+     |$rw       |
        |$rw       |     |>10.to.11 |
        |>10.to.11 |     |10        |
        |10        |     |12        |
        |12        |     |13        |
        |13        |     |>1.to.1   |
        |>1.to.1   |     |1         |
        |1         |     |2         |
        |2         |     |3         |
        |3         |     |#<---Histo|
        +----------+     +----------+
        |4         |     |12        |
        |5         |     |13        |
        |6         |     |>@        |
        |>undo     |     ~          ~
        |@         ~     ~          ~
        +----------+     +----------+
        """)


class UndoScenario(tmux.TmuxPane):
    """
    A series of prompts, inputs, and associated outputs.
    Final line must have a cursor on it.
    """
    def bash_config_contents(self):
        save_addr = rewrite.temp_name('save')
        restore_addr = rewrite.temp_name('restore')
        os.environ['RLUNDO_SAVE'] = save_addr
        os.environ['RLUNDO_RESTORE'] = restore_addr
        return """
        export PS1='$'
        alias rw="python rewrite.py --save-addr %s --restore-addr %s python %s"
        """ % (save_addr, restore_addr, self.python_script.name)

    def python_script_contents(self):
        return open(scenarioscript.__file__).read()

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
        >>> UndoScenario.validate_termstate(termstate)
        Traceback (most recent call last):
            ...
        ValueError: termstate doesn't start with a call to rw: u'>a'
        """
        if not termstate.lines[0] == '$rw':
            raise ValueError("termstate doesn't start with a call to rw: %r" % (termstate.lines[0], ))
        if not termstate.cursor_line == len(termstate.lines) - 1:
            raise ValueError("cursor not on last line!")

    def __enter__(self):
        """Initialize a pane with an undo scenario.

        undo schenarios always start by calling python rewrite.py

        >>> termstate = terminal_dsl.TerminalState(
        ...     ['$rw', '>a', 'b', 'c', '>d', 'e', '>'], cursor_line=6,
        ...     cursor_offset=1, width=10, height=10, history_height=0)
        >>> with UndoScenario(termstate) as t:
        ...     UndoScenario.initialize(t, termstate)
        ...     print(tmux.visible_after_prompt(t, expected=u'>'))
        [u'$rw', u'>a', u'b', u'c', u'>d', u'e', u'>']
        """
        self.python_script = self.tempfile(self.python_script_contents())
        return tmux.TmuxPane.__enter__(self)

    @classmethod
    def initialize(cls, pane, termstate):

        lines = termstate.lines[:]
        assert lines.pop(0) == '$rw'
        tmux.send_command(pane, 'rw', prompt=u'>')
        save()
        first_line = lines.pop(0)
        assert first_line.startswith('>')
        pane.cmd('send-keys', first_line[1:])
        pane.enter()
        tmux.wait_until_cursor_moves(pane, 1, 1)
        for i, line in enumerate(lines):
            if i == termstate.cursor_line:
                assert len(lines) == i - 1
                pane.cmd('send-keys', line)
            elif line.startswith('>'):
                tmux.send_command(pane, '>', enter=False, prompt=u'>')
                save()
                pane.cmd('send-keys', line[1:])
                if i != len(lines) - 1:
                    pane.enter()
            else:
                if line != '':
                    row, col = tmux.cursor_pos(pane)
                    pane.cmd('send-keys', line)
                    tmux.wait_until_cursor_moves(pane, row, col)
                if i != len(lines) - 1:
                    pane.enter()
        row, col = tmux.cursor_pos(pane)

        additional_required_blank_rows = (
            termstate.history_height - len(tmux.scrollback(pane)) +
            termstate.height - row - 1)
        assert additional_required_blank_rows >= 0
        assert col == len(line) % termstate.width  # TODO allow other columns
        if additional_required_blank_rows == 1:
            pane.cmd('1c'+str(col))
            pane.enter()
        elif additional_required_blank_rows > 1:
            for _ in range(additional_required_blank_rows - 1):
                pane.enter()
            for _ in range(additional_required_blank_rows - 2):
                pane.cmd('send-keys', 'up2')
                pane.enter()
            pane.cmd('send-keys', 'uc'+str(col))
            pane.enter()


class TestUndoScenario(unittest.TestCase):
    def test_initialize(self):
        lines = ['$rw', '>a', 'b', 'c', '>d', 'e', '>']
        termstate = terminal_dsl.TerminalState(
            lines, cursor_line=6, cursor_offset=1,
            width=10, height=10, history_height=0)
        with UndoScenario(termstate) as t:
            UndoScenario.initialize(t, termstate)
            output = tmux.visible(t)
            self.assertEqual(output, lines)

    def assertRoundtrip(self, diagram):
        (before, ) = [terminal_dsl.parse_term_state(x)[1]
                      for x in terminal_dsl.divide_term_states(diagram)]
        with UndoScenario(before) as t:
            UndoScenario.initialize(t, before)
            after = terminal_dsl.TerminalState.from_tmux_pane(t)

        self.assertEqual(before, after, before.visible_diff(after))

    def test_wrapped(self):
        self.assertRoundtrip("""
        +------+
        |$rw   |
        +------+
        |>1    |
        |>stuff|
        |abcdef+
        |ghijkl+
        |mnopq |
        |>@    |
        +------+
        """)

    def test_blank_lines(self):
        self.assertRoundtrip("""
        +------+
        |$rw   |
        +------+
        |>1    |
        |>x    |
        |abcde |
        |>@    |
        ~      ~
        ~      ~
        +------+
        """)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
