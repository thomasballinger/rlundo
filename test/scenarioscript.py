import sys
move_up = u'\x1bM'
move_right = u'\x1b[C'
move_left = u'\b'
clear_eol = u'\x1b[K'
clear_eos = u'\x1b[J'

py2 = sys.version_info[0] == 2
if py2:
    input = raw_input


def make_blank_line_below(n):
    "Move cursor back to prev spot after hitting return"
    sys.stdout.write(move_up)
    for _ in range(20):
        sys.stdout.write(move_left)
    for _ in range(n):
        sys.stdout.write(move_right)
    sys.stdout.write(clear_eos)
    sys.stdout.flush()


def move_cursor_back_up():
    sys.stdout.write(move_up)
    sys.stdout.write(move_up)
    sys.stdout.flush()


def move_cursor_up_and_over_and_clear(n):
    sys.stdout.write(move_up)
    sys.stdout.write(move_up)
    for _ in range(20):
        sys.stdout.write(move_left)
    for _ in range(n):
        sys.stdout.write(move_right)
    sys.stdout.write(clear_eos)
    sys.stdout.flush()


def dispatch(prompt=None):
    if prompt:
        inp = input(prompt)
    else:
        inp = input()
    if inp.startswith('1c'):
        make_blank_line_below(int(inp[2:]))
    elif inp == 'up2':
        move_cursor_back_up()
    elif inp.startswith('uc'):
        move_cursor_up_and_over_and_clear(int(inp[2:]))


if __name__ == '__main__':
    dispatch(">")
    while True:
        dispatch()
