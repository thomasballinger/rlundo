from __future__ import unicode_literals

import ast
import os
import unittest

from .context import rlundo
from rlundo import termrewrite

class TestRewriteHelpers(unittest.TestCase):
    def test_history(self):
        self.assertEqual(termrewrite.history(
                         [b'>>> print("hello\\n"*3)\nhello\nhello\nhello\n',
                          b'>>> 1 + 1\n2\n',
                          b'>>> ']),
                         [b'>>> print("hello\\n"*3)',
                          b'hello',
                          b'hello',
                          b'hello',
                          b'>>> 1 + 1',
                          b'2',
                          b'>>> '])

    def test_count_lines(self):
        self.assertEqual(termrewrite.count_lines("1234\n123456", 4), 2)
        self.assertEqual(termrewrite.count_lines("1234\n123456", 10), 1)
        self.assertEqual(termrewrite.count_lines("> undo\r\n> 1\r\n1\r\n", 10), 3)
        self.assertEqual(termrewrite.count_lines("\x01\x1b[0;32m\x02In [\x01\x1b[1;32m\x021\x01\x1b[0;32m\x02]: 1\n\x01\x1b[0m\x02\x1b[0;31mOut[\x1b[1;31m1\x1b[0;31m]: \x1b[0m1\n\n", 40), 3)
        self.assertEqual(termrewrite.count_lines('\r\n\x1b[0;32mIn [\x1b[1;32m2\x1b[0;32m]: \x1b[0mundo\x1b[0;32m   ...: \x1b[0m     \r\n\r\n', 40), 3)

        with open(os.path.join(os.path.dirname(__file__), "input_with_colours.txt"), "r") as f:
            data = ast.literal_eval('u"""'+f.read()+'"""')
        self.assertEqual(termrewrite.count_lines(data, 80), 6)

    def test_linesplit(self):
        self.assertEqual(termrewrite.linesplit(["1234", "123456"], 4),
                         ["1234", "1234", "56"])
        self.assertEqual(termrewrite.linesplit(["1234", "123456"], 10),
                         ["1234", "123456"])

    def test_visible_characters(self):
        self.assertEqual(termrewrite._visible_characters(u"1234"), 4)
        self.assertEqual(termrewrite._visible_characters(u"1234\n"), 4)
        self.assertEqual(termrewrite._visible_characters(u"\x1b[0;32m1234"), 4)
        self.assertEqual(termrewrite._visible_characters(u"\x1b[0m1234"), 4)

    def test_rows_required(self):
        self.assertEqual(termrewrite._rows_required(u"1234", 4), 1)
        self.assertEqual(termrewrite._rows_required(u"1234", 3), 2)
        self.assertEqual(termrewrite._rows_required(u"1234", 2), 2)
        self.assertEqual(termrewrite._rows_required(u"1234", 1), 4)
        self.assertEqual(termrewrite._rows_required(u"\x1b[0;32m1234", 2), 2)
