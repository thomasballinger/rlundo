#rlundo


For a simple demo not requiring c compiling, try

    $ python rewrite.py python undoablepython.py

The goal is for this to work with any interpreter, as in

    $ python rewrite.py rlundo /usr/bin/irb

which will work if you compile a new readline


* rlundoable - a patch for readline that makes it fork to save state
* rewrite.py - a rewinds the terminal state to how it was at the last prompt




##rlundoable

test with 

    $ python rlundo.py /usr/bin/irb


##rewrite

test with 

    $ python rewrite.py

and then in another terminal run

    nc localhost 4242

to save terminal states, and

    nc localhost 4243

to restore previous terminal states


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









For a simple demo not requiring, try

    $ python rewrite.py python undoablepython.py

The goal is for this to work with any interpreter, as in

    $ python rewrite.py rlundo /usr/bin/irb



##Prototype

- [x] run a program in a subprocess, and know what the current state of the terminal screen is.
- [x] keep track of original cursor starting location
- [x] take snapshots of terminal state.
- [x] restore previous snapshots
  - [x] keep track of number of times scrolled down.
    - [x] modify doy's vt100 to keep track of scroll_offset
- [x] start vt100 cursor position where it was when started
- [x] send signal from rlundo program to snapshot and restore states

##The real thing

- [x] write simple version that
  * ignores resizes
  * ignores linewraps (assumes 1 line == 1 row)
  * doesn't query cursor
  * uses relative terminal motions
  * takes instructions from modified readline over sockets

- [ ] set up tests for that simple version

- [ ] set up testing harness: use a GUI terminal emulator 
  - [ ] programmatically set up tmux
    - [ ] programmatically set up tmux
  - [ ] request state of scrollback buffer and screen
  - [ ] write a simple test
  - [ ] implement cursor query to discover how cursor moved
  - [ ] terminal detection via env TERM and database for wrap strategies

- Test cases:
  - [ ] same screen, no line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll down, no line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: same screen, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll down, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll off of the screen, no line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll off the screen, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: screen resize
    - [ ] write test
    - [ ] test passing

