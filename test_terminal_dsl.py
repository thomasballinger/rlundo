from terminal_dsl import TerminalState, parse_term_state, horzcat
import unittest


class TestTerminalDiagramParsing(unittest.TestCase):
    def test_parse_term_state(self):
        s = """
        +------+
        +------+
        |a-a-a-|
        |b-b-b-|
        |@     |
        +------+"""
        self.assertEqual(parse_term_state(s), ('', TerminalState(
            lines=['a-a-a-', 'b-b-b-', ''],
            cursor_line=2,
            cursor_offset=0,
            width=6,
            height=3,
            history_height=0)))

    def test_parse_term_state_with_empty_lines(self):
        s = """
        +------+
        +------+
        |a-a-a-|
        |b-b-b-|
        |@     |
        ~      ~
        ~      ~
        +------+"""
        self.assertEqual(parse_term_state(s), ('', TerminalState(
            lines=['a-a-a-', 'b-b-b-', ''],
            cursor_line=2,
            cursor_offset=0,
            width=6,
            height=5,
            history_height=0)))

    def test_parse_term_state_input_rejection(self):
        s = """
        +------+
        ~      ~
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


class TestHelpers(unittest.TestCase):
    def test_horzcat(self):
        self.assertEqual(horzcat('a\nbc\ndef\ng',
                                 'z\nx\nywvut'),
                         'a  z\nbc x\ndefywvut\ng  ')
