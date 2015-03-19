"""
Terminal diagrams for describing how text is moved when the window of a
terminal emulator is resized.

# @ is cursor
# + means this is a continued line
# . means a space character (spaces are empty)
# everything else is content
# lowercase letters are in the app's control

A diagram looks like this:
    +-----+
    |ABC  |
    +-----+
    |BC   |
    |abc@ |
    |     |
    +-----+

"""

from functools import partial
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
    ... |     |    |       |
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
    diagrams = [s for s in candidates if '|' in s and '-' in s and '@' in s]
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


class TerminalState(_TerminalStateBase):
    @classmethod
    def from_redundant_information(cls):
        """Uses extra parameters to check derived properties"""
        pass

    @property
    def visible_rows(self):
        return split_lines(self.lines, self.width)[self.history_height:]

    @property
    def history_rows(self):
        return split_lines(self.lines, self.width)[:self.history_height]

    @property
    def cursor_row(self):
        pass

    @property
    def cursor_column(self):
        pass


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
    ... |           |
    ... +-----------+
    ... ''')
    >>> label
    'label'
    >>> state.width
    11
    >>> state.lines
    ['1234567890123456789', '$ echo hi', 'hi', '$ python', '>>> 1 + 1', '2', '', '']
    >>> state.history_rows
    ['12345678901', '23456789', '$ echo hi']
    >>> state.visible_rows
    ['hi', '$ python', '>>> 1 + 1', '2', '', '']
    >>> (state.cursor_line, state.cursor_offset)
    (6, 0)

    #>>> (state.cursor_row, state.cursor_column)
    #(7, 0)
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

    input_rows = re.findall(r'(?<=\n)\s*([+|].*[+!|])\s*(?=\n|\Z)', s)
    for input_row in input_rows:
        inner = input_row[1:-1]
        if inner == '-'*width:
            section = sections[sections.index(section) + 1]
            if section == 'after':
                break
            continue
        else:
            section_heights[section] += 1

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



def asdf():
    m = re.search(r'(?<=\n)\s*([+][-]+[+])\s*(?=\n)', s)
    label = ' '.join(line.strip() for line in s[:m.start()].split('\n') if line.strip())
    top_border = m.group(1)
    width = len(top_border) - 2
    assert width > 0
    input_rows = re.findall(r'(?<=\n)\s*([+|].*[+!|])\s*(?=\n|\Z)', s)
    for input_row in input_rows:
        if len(input_row) - 2 != width:
            raise ValueError("terminal diagram row not of width %d: %r" % (width + 2, input_row,))

    sections = ('before', 'history', 'visible', 'after')
    section = sections[0]
    current_visible_row = -1
    maybe_for_visible = []
    maybe_for_rendered = []

    history = []
    rendered = []
    visible = []
    cursor = None
    top_usable_row = 0

    for input_row in input_rows:
        inner = input_row[1:-1]
        if inner == '-'*width:
            section = sections[sections.index(section) + 1]
            if section == 'after':
                break
            continue

        if section == 'visible':
            current_visible_row += 1

        if '@' in inner:
            if cursor is not None:
                raise ValueError("Two cursors (@'s) in terminal diagram:\n%s" % (s,))
            cursor = (current_visible_row, inner.index('@'))
            inner = inner.replace('@', ' ')

        if section == 'history':
            history.append(inner.lower().rstrip())
        elif section == 'visible':
            if inner.strip():
                visible.extend(maybe_for_visible)
                del maybe_for_visible[:]
                visible.append(inner.lower().rstrip())
            else:
                maybe_for_visible.append(inner.lower().rstrip())
        elif section == 'after':
            break
        elif section == 'before':
            continue

        if inner.strip():
            if is_lower(inner):
                if section == 'history':
                    scrolled += 1
                    scrolled += len(maybe_for_rendered)
                rendered.extend(maybe_for_rendered)
                rendered.append(inner.rstrip())
                del maybe_for_rendered[:]
            elif is_upper(inner) and section == 'visible':
                top_usable_row += 1
        else:
            maybe_for_rendered.append(inner.strip())

    if not section == 'after':
        raise ValueError("finish in section %s - didn't complete terminal diagram:\n%s" % (section, s))
    if cursor is None:
        raise ValueError("No cursor found (@) in terminal diagram:\n%s" % (s,))

    return (label,
            TerminalState(history=history, rendered=rendered,
                          top_usable_row=top_usable_row, scrolled=scrolled,
                          cursor=cursor, visible=visible,
                          rows=current_display_line+1, columns=width))

def line_is(type, line):
    has_upper = bool(re.search('[A-Z]', line))
    has_lower = bool(re.search('[a-z]', line))
    if has_upper and has_lower:
        raise ValueError('Both uppercase and lowercase letters in terminal diagram line: %r' % (line,))
    elif not has_upper and not has_lower:
        raise ValueError('no uppercase or lowercase letters in terminal diagram line: %r' % (line,))
    elif type == 'upper' and has_upper and not has_lower:
        return True
    elif type == 'lower' and has_lower and not has_upper:
        return True
    else:
        return False

is_lower = partial(line_is, 'lower')
is_upper = partial(line_is, 'upper')


# should eventually test xterm, gnome-terminal, iterm, terminal.app, tmux

#terminal questions:
# * does xterm have a difference between spaces and nothing?
# * does xterm do cursor at bottom scroll up differently?
# * can xterm ever have a clear space at bottom but history

if __name__ == '__main__':
    import doctest
    doctest.testmod()
