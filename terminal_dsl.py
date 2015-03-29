"""
Terminal diagrams for describing how text is moved when the window of a
terminal emulator is resized.

# @ is cursor
# + means this is a continued line
# . means a space character (spaces are empty)
# ~ means this line is empty (no content on line, no newline on prev line)
# everything else is content

A diagram looks like this:
    +-----+
    |ABC  |
    +-----+
    |BC   |
    |abc@ |
    |     |
    +-----+

"""

import unittest
import re
from collections import namedtuple

def divide_term_states(s):
    """Return a list of vertically divided terminal diagrams from one string

    >>> len(divide_term_states('''
    ... +-----+    +-------+   +--+
    ... |ABC  |    |ABC    |   +--+
    ... +-----+    +-------+   |@ |
    ... |BC   | -> |BC     |   +--+
    ... |abc@ |    |abc@   |
    ... |~    |    |~      |
    ... +-----+    +-------+
    ... '''))
    3
    """
    # TODO allow the first line to have content on it (has to be blank right now)
    lines = s.split('\n')
    if lines[0].strip():
        raise ValueError('Top line needs to be blank')
    max_length = max(len(line) for line in lines)
    spaces_by_line = [set(m.start() for m in re.finditer(r' ', line)).union(
                          set(range(len(line), max_length)))
                      for line in s.split('\n') if s.strip()]
    empty_columns = set.intersection(*spaces_by_line)
    empty_columns.add(max_length)

    sections = []
    last = 0
    for index in sorted(empty_columns):
        vertical_strip = []
        for line in s.split('\n'):
            vertical_strip.append(line[last:index])
        sections.append(vertical_strip)
        last = index
    candidates = ['\n'.join(section) for section in sections]
    diagrams = [x for x in candidates if '|' in x and '-' in x and '+' in x]
    return diagrams

_TerminalStateBase = namedtuple('TerminalState', [
    'lines',          # logical lines of history and content
    'cursor_line',    # 0-indexed logical line of cursor
    'cursor_offset',  # position in logical line of first character
    'width',          # number of columns
    'height',         # number of visible rows
    'history_height'  # number of history rows
])


def split_line(line, width):
    """
    >>> split_line('abcdefg', 3)
    ['abc', 'def', 'g']
    """
    if line == '':
        return ['']
    splits = range(0, len(line), width) + [len(line)]
    return [line[start:end] for start, end in zip(splits[:-1], splits[1:])]


def split_lines(lines, width):
    """
    >>> split_lines(['abcd', 'e', 'fgh', ''], 3)
    ['abc', 'd', 'e', 'fgh', '']
    """
    rows = []
    for line in lines:
        rows.extend(split_line(line, width))
    return rows


def horzcat(a, b):
    a_lines = a.split('\n')
    b_lines = b.split('\n')
    width = max(len(line) for line in a_lines)
    full_lines = [line + ' '*(width - len(line)) for line in a_lines]
    full_left = full_lines + [' '*width] * max(0, len(b_lines) - len(a_lines))
    full_right = b_lines + [''] * max(0, len(a_lines) - len(b_lines))
    assert len(full_left) == len(full_right)
    return '\n'.join(l+r for l, r in zip(full_left, full_right))


class TerminalState(_TerminalStateBase):

    @classmethod
    def from_tmux_pane(cls, pane):
        import tmux
        lines = tmux.all_lines(pane)
        history_height = len(tmux.scrollback(pane))
        print 'tmux.all_contents:', tmux.all_contents(pane)
        print 'tmux.visible:', tmux.visible(pane)
        print 'history_height:', history_height
        print 'tmux.scrollback:', tmux.scrollback(pane)
        width, height = tmux.width(pane), tmux.height(pane)

        cursor_row, cursor_col = tmux.cursor_pos(pane)

        #TODO deal with cursors not at the bottom

        termstate = TerminalState(
            lines=lines,
            cursor_line=len(lines) - 1,
            cursor_offset=len(lines[-1]),
            width=width,
            height=height,
            history_height=history_height)
        print termstate

        #assert termstate.cursor_row == cursor_row
        #assert termstate.cursor_column == cursor_col

        return termstate

    def visible_diff(self, other):
        if self != other:
            s1, s2 = self.render(), other.render()
            display = horzcat(s1, s2)
            if len(self.lines) != len(other.lines):
                error = ('Terminal states have different number of lines:'
                         '%d and %d' % (len(self.lines), len(other.lines)))
            elif self.lines != other.lines:
                for i, (a, b) in enumerate(zip(self.lines, other.lines)):
                    if a != b:
                        error = "line %d is the first line to differ:" % (i, )
                        break
            else:
                error = "Terminal states differ somehow:"
            return error + '\n' + display + '\n' + repr(self) + '\n' + repr(other)
        return 'TerminalStates do not differ'

    def render(self):
        horz_border = '+' + '-'*self.width + '+'
        output = []
        output.append(horz_border)
        row_num = -1
        in_history = True
        cursor_row, cursor_col = self.cursor_row, self.cursor_column
        cursor_row = self.cursor_row
        for line in self.lines:
            line_rows = []
            for row in split_line(line, self.width):
                row_num += 1
                if in_history and row_num == self.history_height:
                    output.append(horz_border)
                    row_num = 0
                    in_history = False
                if not in_history and row_num == cursor_row:
                    row = row[:cursor_row] + '@' + row[cursor_col+1:]
                line_rows.append('|' + row + ' '*(self.width - len(row)) + '|')
            line_rows = ([r[:-1]+'+' for r in line_rows[:len(line_rows)-1]] +
                         [line_rows[-1]])

            output.extend(line_rows)
        while row_num < self.height - 1:
            output.append('~' + ' '*self.width + '~')
            row_num += 1
        output.append(horz_border)
        return '\n'.join(output)

    @property
    def visible_rows(self):
        return split_lines(self.lines, self.width)[self.history_height:]

    @property
    def history_rows(self):
        return split_lines(self.lines, self.width)[:self.history_height]

    @property
    def cursor_row(self):
        """one-indexed"""
        above = len(split_lines(self.lines[:self.cursor_line], self.width))
        rows, _ = divmod(len(self.lines[self.cursor_line][:self.cursor_offset+1]), self.width)
        return above - self.history_height + rows + 1

    @property
    def cursor_column(self):
        """one-indexed"""
        _, offset = divmod(len(self.lines[self.cursor_line][:self.cursor_offset+1]), self.width)
        return offset + 1


def parse_term_state(s):
    """Returns TerminalState tuple given a terminal state diagram

    >>> label, state = parse_term_state('''
    ...     label
    ... +-----------+
    ... |12345678901+
    ... |23456789   |
    ... |$ echo hi  |
    ... +-----------+
    ... |hi         |
    ... |$ python   |
    ... |>>> 1 + 1  |
    ... |2          |
    ... |@          |
    ... ~           ~
    ... +-----------+
    ... ''')
    >>> label
    'label'
    >>> state.width
    11
    >>> state.lines
    ['1234567890123456789', '$ echo hi', 'hi', '$ python', '>>> 1 + 1', '2', '']
    >>> state.history_rows
    ['12345678901', '23456789', '$ echo hi']
    >>> state.visible_rows
    ['hi', '$ python', '>>> 1 + 1', '2', '']
    >>> (state.cursor_line, state.cursor_offset)
    (6, 0)
    >>> (state.cursor_row, state.cursor_column)
    (5, 1)
    """

    top_border_match = re.search(r'(?<=\n)\s*([+][-]+[+])\s*(?=\n)', s)
    label = ' '.join(line.strip()
                     for line in s[:top_border_match.start()].split('\n')
                     if line.strip())
    top_border = top_border_match.group(1)
    width = len(top_border) - 2

    sections = ('before', 'history', 'visible', 'after')
    section = sections[0]
    lines = []
    unfinished_line = None
    section_heights = dict(zip(sections, [0] * len(sections)))

    input_rows = re.findall(r'(?<=\n)\s*([+|~].*[+|~])\s*(?=\n|\Z)', s)
    if not all(len(input_rows[0]) == len(r) for r in input_rows):
        raise ValueError('row differs in width from first')
    for input_row in input_rows:
        inner = input_row[1:-1]
        if inner == '-'*width:
            section = sections[sections.index(section) + 1]
            if section == 'after':
                break
            continue
        else:
            section_heights[section] += 1

        if input_row[0] == input_row[-1] == '~':
            if not section == 'visible':
                raise ValueError('~ in non-visible section')
            continue

        if input_row[-1] == '+':
            if unfinished_line is None:
                unfinished_line = ''
            unfinished_line += inner
        else:
            if unfinished_line is None:
                lines.append(inner.rstrip())
            else:
                unfinished_line += inner.rstrip()
                lines.append(unfinished_line)
                unfinished_line = None
    else:
        raise ValueError("not enough sections, didn't finish parsing")
    if unfinished_line is not None:
        lines.append(unfinished_line)

    for cursor_line, line in enumerate(lines):
        if '@' in line:
            cursor_offset = line.index('@')
            lines[cursor_line] = line.replace('@', '')
            break
    else:
        raise ValueError("No cursor (@) found")

    return label, TerminalState(
        lines=lines,
        cursor_line=cursor_line,
        cursor_offset=cursor_offset,
        width=width,
        height=section_heights['visible'],
        history_height=section_heights['history'],
    )



# should eventually test xterm, gnome-terminal, iterm, terminal.app, tmux

#terminal questions:
# * does xterm have a difference between spaces and nothing?
# * does xterm do cursor at bottom scroll up differently?
# * can xterm ever have a clear space at bottom but history

if __name__ == '__main__':
    import doctest
    doctest.testmod()
