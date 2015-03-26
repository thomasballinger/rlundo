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

test with 

    $ python rlundo.py /usr/bin/irb


##rewrite.py

test with 

    $ python rewrite.py

and then in another terminal run

    nc localhost 4242

to save terminal states, and

    nc localhost 4243

to restore previous terminal states


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
    [ ] record logical lines of history in addition to rows
  - put new prompt in middle row if there's enough history to fill out above it
  - put new prompt higher up if not enough history

- [ ] set up testing harness: use Tmux
  - [x] programmatically set up tmux
    - [ ] programmatically set up terminal state from a diagram
  - [x] request state of scrollback buffer and screen
  - [x] write a simple test
  - [x] implement cursor query to discover how cursor moved
    - [x] test cursor query with tmux
  - [x] count lines from sequence
    - [ ] also use width to calculate
  - [x] figure out if wrapping works (I'm suspicious it doesn't,
        and we'll need calculate wrapping ourselves

- Test cases:
  - [x] same screen, no line wrapping
    - [x] write test
    - [x] test passing
  - [ ] test case: same screen, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll down, no line wrapping
    - [x] write test
    - [x] test passing
  - [ ] test case: scroll down, line wrapping
    - [ ] write test
    - [ ] test passing
  - [ ] test case: scroll off of the screen, no line wrapping
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
