from terminal_dsl import TestTerminalResizing, TerminalState, parse_term_state, divide_term_states
import unittest

class TestTestTerminalResizing(unittest.TestCase, TestTerminalResizing):
    def test_simple(self):
        self.actions = []
        self.assertResizeMatches("""
        +--+   +--+
        +--+   +--+
        |a |   |a |
        |b@|   |b@|
        +--+   +--+
        """)
        self.assertTrue(word +' called' in self.actions
                        for word in ['prepare_terminal', 'render', 'resize', 'check_output'])
    def prepare_terminal(self, rows, columns, history, visible, cursor, rendered, top_usable_row):
        self.actions.append('prepare_terminal called')
    def render(self, array, cursor):
        self.actions.append('render called')
    def resize(self, rows, columns):
        self.actions.append('resize called')
    def check_output(self, *args):
        self.actions.append('check_output called')

class TestTerminalDiagramParsing(unittest.TestCase):
    def test_parse_term_state(self):
        s = """
        +------+
        +------+
        |a-a-a-|
        |b-b-b-|
        |@-c-c-|
        +------+"""
        self.assertEqual(parse_term_state(s), ('', TerminalState(
            history=[],
            rendered=['a-a-a-', 'b-b-b-', ' -c-c-'],
            top_usable_row=0,
            scrolled=0,
            cursor=(2, 0),
            visible=['a-a-a-', 'b-b-b-', ' -c-c-'],
            rows=3,
            columns=6)))
    def test_parse_term_state_input_rejection(self):
        s = """
        +------+
        +------+
        |1-1-1-|
        |2-2-2-|
        |@-3-3-|
        +------+"""
        self.assertRaises(ValueError, parse_term_state, s)
        s = """
        +------+
        |a-a-a-|
        |b-b-b-|
        |@-c-c-|
        +------+"""
        self.assertRaises(ValueError, parse_term_state, s)
        s = """
        +------+
        +------+
        |a-a-a-|
        |b-b-b-|
        |c-c-c-|
        +------+"""
        self.assertRaises(ValueError, parse_term_state, s)

