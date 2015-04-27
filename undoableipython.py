#!/usr/bin/env python

import os
import sys
from IPython.utils import py3compat
import bdb
from IPython.utils.warn import warn
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython import start_ipython
from IPython.utils.text import num_ini_spaces


def rl_is_ipython(rl_path):
    return os.path.basename(rl_path) == "ipython"


def interact(self, display_banner=None):
    """Closely emulate the interactive Python console."""

    # ----------------------------------
    # ----------------------------------
    # HERE WE ARE REPLACING IPYTHON CODE
    # ----------------------------------
    # ----------------------------------
    from functools import partial
    import socket

    if sys.version_info.major == 2:
        ConnectionRefusedError = socket.error

    def connect_and_wait_for_close(port):
        s = socket.socket()
        try:
            s.connect(('localhost', port))
        except ConnectionRefusedError:
            pass
        else:
            assert b'' == s.recv(1024)

    save = partial(connect_and_wait_for_close, port=4242)
    restore = partial(connect_and_wait_for_close, port=4243)
    # -------------------------------------
    # -------------------------------------
    # HERE WE FINISH REPLACING IPYTHON CODE
    # -------------------------------------
    # -------------------------------------

    # batch run -> do not interact
    if self.exit_now:
        return

    if display_banner is None:
        display_banner = self.display_banner

    if isinstance(display_banner, py3compat.string_types):
        self.show_banner(display_banner)
    elif display_banner:
        self.show_banner()

    more = False

    if self.has_readline:
        self.readline_startup_hook(self.pre_readline)
        hlen_b4_cell = self.readline.get_current_history_length()
    else:
        hlen_b4_cell = 0
    # exit_now is set by a call to %Exit or %Quit, through the
    # ask_exit callback.

    while not self.exit_now:
        # import pudb; pudb.set_trace()
        self.hooks.pre_prompt_hook()
        if more:
            try:
                # import pudb; pudb.set_trace()
                prompt = self.prompt_manager.render('in2')
            except:
                self.showtraceback()
            if self.autoindent:
                self.rl_do_indent = True

        else:
            try:
                # import pudb; pudb.set_trace()
                prompt = self.separate_in + \
                    self.prompt_manager.render('in')
            except:
                self.showtraceback()
        try:
            # import pudb; pudb.set_trace()

            # ----------------------------------
            # ----------------------------------
            # HERE WE ARE REPLACING IPYTHON CODE
            # ----------------------------------
            # ----------------------------------
            while True:
                save()
                try:
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++
                    # This is the only ipython line of code in this block
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++
                    line = self.raw_input(prompt)
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++
                    # This is the only ipython line of code in this block
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++
                except KeyboardInterrupt:
                    line = "undo"

                if line == "undo":
                    restore()
                    os._exit(42)

                pid = os.fork()
                is_child = pid == 0

                # if the process is not the parent, just carry on
                if is_child:
                    break

                else:
                    while True:
                        try:
                            status = os.waitpid(pid, 0)
                            break
                        except KeyboardInterrupt:
                            pass
                    exit_code = status[1] // 256
                    if not exit_code == 42:
                        os._exit(exit_code)

            # -------------------------------------
            # -------------------------------------
            # HERE WE FINISH REPLACING IPYTHON CODE
            # -------------------------------------
            # -------------------------------------

            if self.exit_now:
                # quick exit on sys.std[in|out] close
                break
            if self.autoindent:
                self.rl_do_indent = False

        except KeyboardInterrupt:
            # double-guard against keyboardinterrupts during kbdint
            # handling
            try:
                self.write('\n' + self.get_exception_only())
                source_raw = self.input_splitter.raw_reset()
                hlen_b4_cell = \
                    self._replace_rlhist_multiline(
                        source_raw, hlen_b4_cell)
                more = False
            except KeyboardInterrupt:
                pass
        except EOFError:
            if self.autoindent:
                self.rl_do_indent = False
                if self.has_readline:
                    self.readline_startup_hook(None)
            self.write('\n')
            self.exit()
        except bdb.BdbQuit:
            warn('The Python debugger has exited with a BdbQuit exception.\n'
                 'Because of how pdb handles the stack, it is impossible\n'
                 'for IPython to properly format this particular exception.\n'
                 'IPython will resume normal operation.')
        except:
            # exceptions here are VERY RARE, but they can be triggered
            # asynchronously by signal handlers, for example.
            self.showtraceback()
        else:
            try:
                self.input_splitter.push(line)
                more = self.input_splitter.push_accepts_more()
            except SyntaxError:
                # Run the code directly - run_cell takes care of displaying
                # the exception.
                more = False
            if (self.SyntaxTB.last_syntax_error and
                    self.autoedit_syntax):
                self.edit_syntax_error()
            if not more:
                source_raw = self.input_splitter.raw_reset()
                self.run_cell(source_raw, store_history=True)
                hlen_b4_cell = \
                    self._replace_rlhist_multiline(
                        source_raw, hlen_b4_cell)

    # Turn off the exit flag, so the mainloop can be restarted if desired
    self.exit_now = False


def raw_input_original(prompt):

    from functools import partial
    import socket

    if sys.version_info.major == 2:
        ConnectionRefusedError = socket.error

    def connect_and_wait_for_close(port):
        s = socket.socket()
        try:
            s.connect(('localhost', port))
        except ConnectionRefusedError:
            pass
        else:
            assert b'' == s.recv(1024)

    save = partial(connect_and_wait_for_close, port=4242)
    restore = partial(connect_and_wait_for_close, port=4243)

    while True:
        save()
        try:
            if py3compat.PY3:
                line = input(prompt)
            else:
                line = raw_input(prompt)
        except KeyboardInterrupt:
            line = "undo"

        if line == "undo":
            restore()
            os._exit(42)

        pid = os.fork()
        is_child = pid == 0

        # if the process is not the parent, just carry on
        if is_child:
            break

        else:
            while True:
                try:
                    status = os.waitpid(pid, 0)
                    break
                except KeyboardInterrupt:
                    pass
            exit_code = status[1] // 256
            if not exit_code == 42:
                os._exit(exit_code)

    return line


def raw_input_replacement(self, prompt=''):
    """Write a prompt and read a line.

    The returned line does not include the trailing newline.
    When the user enters the EOF key sequence, EOFError is raised.

    Parameters
    ----------

    prompt : str, optional
      A string to be printed to prompt the user.
    """
    # raw_input expects str, but we pass it unicode sometimes
    prompt = py3compat.cast_bytes_py2(prompt)

    try:
        line = py3compat.str_to_unicode(raw_input_original(prompt))
    except ValueError:
        warn("\n********\nYou or a %run:ed script called sys.stdin.close()"
             " or sys.stdout.close()!\nExiting IPython!\n")
        self.ask_exit()
        return ""

    # Try to be reasonably smart about not re-indenting pasted input more
    # than necessary.  We do this by trimming out the auto-indent initial
    # spaces, if the user's actual input started itself with whitespace.
    if self.autoindent:
        if num_ini_spaces(line) > self.indent_current_nsp:
            line = line[self.indent_current_nsp:]
            self.indent_current_nsp = 0

    return line


def patch_ipython():
    # TerminalInteractiveShell.interact = interact
    # TerminalInteractiveShell.raw_input_original = property(raw_input_original)
    TerminalInteractiveShell.raw_input = raw_input_replacement


def start_undoable_ipython(args=None):
    patch_ipython()

    if args:
        sys.argv = args

    start_ipython()


if __name__ == '__main__':
    start_undoable_ipython()
