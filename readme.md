[![Build Status](https://travis-ci.org/thomasballinger/rlundo.svg?branch=master)](https://travis-ci.org/thomasballinger/rlundo)

#rlundo

rlundo grants interactive interpreters magical undo powers!
Some interpreters work without requiring compiling
a new readline library:

    $ python rlundo python
    $ python rlundo ipython

You can undo using ctrl+c

![undo with ctrl+c](http://ballingt.com/assets/undoable_ipython.gif)

The goal is for this to work with any interpreter, as in

    $ python rlundo /usr/bin/irb

![rlundo preview example](http://ballingt.com/assets/rlundopreview.gif)

which will work if you compile the modified readline library with

    cd rlundoable
    make -f Makefileosx

There are three major parts to this project:

* rlundoable - a patch for readline that makes it fork to save state
* rewrite.py - rewinds the terminal state to how it was at the last prompt
* undoableINTERPRETER - alternative scripts for running specific interactive interpreters so that they have undo

##rlundoable

try it with 

    $ python rlundo /usr/bin/irb


##rewrite.py

try it with 

    $ python rewrite.py

and then in another terminal run

    nc localhost 4242

to save terminal states, and

    nc localhost 4243

to restore previous terminal states

##Running the tests

* clone the repo, create a virtual environment
* pip install nose
* install tmux 2.0
* `nosetests tests` in the root directory
* try `RLUNDO_USE_EXISTING_TMUX_SESSION=1 nosetests tests` while you have a tmux
  session open to watch the tests which use tmux run


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
