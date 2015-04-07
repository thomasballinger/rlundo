#rlundo




For a simple demo not requiring c compiling, try

    $ python rewrite.py python undoablepython.py

The goal is for this to work with any interpreter, as in

    $ python rlundo.py /usr/bin/irb

which will work if you compile a new readline


![rlundo preview example](http://ballingt.com/assets/rlundopreview.gif)


* rlundoable - a patch for readline that makes it fork to save state
* rewrite.py - rewinds the terminal state to how it was at the last prompt

##rlundoable

try it with 

    $ python rlundo.py /usr/bin/irb


##rewrite.py

try it with 

    $ python rewrite.py

and then in another terminal run

    nc localhost 4242

to save terminal states, and

    nc localhost 4243

to restore previous terminal states

##Running the tests

* nosetests
* you're need to install a recent version of tmux, 1.9a seems to work


#Task list

##rewrite.py

- [x] write simple version that
  * ignores resizes
  * ignores linewraps (assumes 1 line == 1 row)
  * doesn't query cursor
  * uses relative terminal motions
  * takes instructions from modified readline over sockets

- [x] set up tests for that simple version
- [x] decide what correct behavior for a scroll-up that goes off screen is
  - "output inconsistent" added to scrollback
  - save history
    [x] calculate logical lines of history from to rows
  - [x] put new prompt in middle row if there's enough history to fill out above it
  - [x] put new prompt higher up if not enough history
- [x] fix prompts not appearing until keystroke
  - [ ] contribute this back to python_termcast_client
- [ ] fix cursor query responses appearing onscreen
- [x] fix pity to allow window resizing (it was a py2/3 problem)
- [ ] fix requiring keystroke at program exit
  - it seems to be something racy - removing logging statements in
    pity makes it happen more!
- [ ] refactor rewrite.py to use a class instead of globals
- [x] set up testing harness: use Tmux
  - [x] programmatically set up tmux
    - [x] programmatically set up terminal state from a diagram
  - [x] request state of scrollback buffer and screen
  - [x] write a simple test
  - [x] implement cursor query to discover how cursor moved
    - [x] test cursor query with tmux
  - [x] count lines from sequence
    - [x] also use width to calculate
  - [x] figure out if wrapping works (I'm suspicious it doesn't,
        and we'll need calculate wrapping ourselves
  - [x] slow mode: does tmux test visible, with delay
  - [x] display test failures with pretty diffs
- [ ] Python 3 compatibility
- [ ] deal with using reverse-iterative-search (currently results
      in clearing too many lines)
- [ ] Watch https://www.youtube.com/watch?t=544&v=EpYMRd1ZWDM and learn lessons from it!
- [ ] Redo (run most recently undone command)
- [ ] Add undone commands to parent process rl history

- Test cases:
  - [x] same screen, no line wrapping
    - [x] write test
    - [x] test passing
  - [x] test case: same screen, line wrapping
    - [x] write test
    - [x] test passing
  - [x] test case: scroll down, no line wrapping
    - [x] write test
    - [x] test passing
  - [ ] test case: scroll down, line wrapping
    - [ ] write test
    - [ ] test passing
  - [x] test case: scroll off of the screen, no line wrapping
    - [x] write test
    - [x] test passing
  - [ ] test case: scroll off the screen, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: undo would move cursor above screen, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: screen resize
    - [ ] write test
    - [ ] test passing
  - [ ] test case: non-1 character widths

##rlundoable

- [ ] ruby crashes if ctrl-d (freeing things?)
- [ ] come up with better ipc than sockets, or check if sockets free
- [ ] make graphs of memory use, annotated with when GCs happen
  - [ ] figure out how to measure memory of interpreters
  - [ ] come up with a reasonable REPL task to benchmark (use other benchmarks?)
    - [ ] trying out syntax (inc. errors)
    - [ ] web scraping
- [ ] use ctrl key instead of typing 'undo'
- [ ] figure out how to intercept Python readline
- [ ] make ctrl-c work in undoablepython.py
- [ ] solution for haskeline



---

##License

Copyright 2015 Thomas Ballinger

Released under GPL3, like GNU readline.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
