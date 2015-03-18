from terminal_dsl import TerminalState, parse_term_state, divide_term_states
import unittest

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

