import argparse

from rlundo.termrewrite import run_with_listeners

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run a command in a pty, saving and restoring the terminal state")
    parser.add_argument('--save-addr', action='store', default=None)
    parser.add_argument('--restore-addr', action='store', default=None)
    parser.add_argument('command', nargs='*')
    args = parser.parse_args()
    if args.command == []:
        args.command = ['python', '-c', "while True: (raw_input if '' == b'' else input)('>')"]
    run_with_listeners(args.command, save_addr=args.save_addr, restore_addr=args.restore_addr)
