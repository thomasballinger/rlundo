[![Build Status](https://travis-ci.org/thomasballinger/rlundo.svg?branch=master)](https://travis-ci.org/thomasballinger/rlundo)

#rlundo

rlundo grants interactive interpreters magical undo powers!

A patched version of readline is used to fork an interpreter
at each prompt. If the user enters `undo` then that child process dies
and execution is resume.

rlundo also removes the terminal output that occured in the late child
process, restoring the terminal to its previous state.

![rlundo preview example](http://ballingt.com/assets/rlundopreview.gif)

The goal is for this to work with any interpreter:

    $ python rlundo /usr/bin/irb

---

Using a patched version of the readline library only works for interactive
interpreters that already use readline. To address this, this project
includes shims for various interpreters that implement undo via fork in a
less general way in /rlundo/interps/. Compiling the patched readline library
is not required for interpreters implemented this way.

    $ python rlundo python
    $ python rlundo ipython

![undo with ctrl+c](http://ballingt.com/assets/undoable_ipython.gif)

##Modified Readline library

rlundoable is a patched readline library with the following modification:
* calling readline causes the process to fork
* the user entering "undo" causes the process to die
* tcp socket connections are made when the process forks or dies to notifiy
  a listener that might be recording terminal state

To build this patched readline library:

    cd rlundoable
    make -f Makefileosx

Read more about the patched readline library in that [readme](rlundoable/readme.md).

##Rewriting terminal state

In order to restore prior terminal state on undo, interpreters are run
in a psuedoterminal that takes snapshots of terminal state when the
interpreter forks and restores previous terminal state when an interpreter
process dies.

try it with

    $ python rewrite.py

and then in another terminal run

    nc localhost 4242

to save terminal states, and

    nc localhost 4243

to restore previous terminal states


#Running the tests

* clone the repo, create a virtual environment
* pip install nose
* install [tmux](https://github.com/tmux/tmux) 1.9a or 2.1 (master). 1.8 is
  too early, 2.0 has a regression.
* `nosetests test` in the root directory
* or try `RLUNDO_USE_EXISTING_TMUX_SESSION=1 nosetests test` while you have a tmux
  session open to watch the tests which use tmux run


---

Thanks to

* John Hergenroeder for help with fixing race conditions with terminal
  rewriting
* John Connor for discussion and Python 3 fixes
* Agustín Benassi for ipython support, improved terminal rewriting, memory
  monitoring work and much more
* Joe Jean for work on Travis tests
* Madelyn Freed for work on the exectuable rlundo script

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
