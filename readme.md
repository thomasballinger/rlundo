[![Build Status](https://travis-ci.org/thomasballinger/rlundo.svg?branch=master)](https://travis-ci.org/thomasballinger/rlundo)

#rlundo

rlundo grants interactive interpreters magical undo powers!

![rlundo preview example](http://ballingt.com/assets/rlundopreview.gif)

For a long read about the motivation for such a tool, see [this blog
post](http://ballingt.com/interactive-interpreter-undo)

A patched version of readline is used to fork an interpreter
at each prompt. If the user enters `undo` then that child process dies
and execution is resume.
rlundo also removes the terminal output that occurred in the recently-deceased
child process, restoring the terminal to its previous state.

The goal is for this to work with any interpreter:

    $ python rlundo irb

The name rlundo is modeled off of
[rlwrap](https://github.com/hanslub42/rlwrap), which wraps interactive
command line interfaces with the readline editing interface. Like that
command, rlundo wraps other interactive interfaces.
To make the analogy work better it probably should have been called undowrap, or
rlundowrap to suggest that the way undo is implemented uses readline.

---

Using a patched version of the readline library only works for interactive
interpreters that dynamically link readline. To address this, this project
includes shims for various interpreters that implement undo via fork in a
less general way in /rlundo/interps/. Compiling the patched readline library
is not required for interpreters implemented this way. Add your favorite!

    $ python rlundo python

(python seems to usually statically link readline)

##Modified Readline library

rlundoable is a patched version of the gnu readline library with the following
modifications:

* calling readline causes the process to fork
* the user entering "undo" causes the process to die
* tcp socket connections are made when the process forks or dies to notify
  a listener that might be recording terminal state

To build this patched readline library:

    cd rlundoable
    make -f Makefileosx

Read more about the patched readline library in that [readme](rlundoable/readme.md).

The library substitution works more reliably for me on linux right now. Maybe
this is because homebrew more often links readline statically? That's just
speculation. Writing workarounds for common interpreters or digging into how
to make readline hijacking more reliable would both be really helpful!

##Rewriting terminal state

In order to restore prior terminal state on undo, interpreters are run
in a pseudo terminal that takes snapshots of terminal state when the
interpreter forks and restores previous terminal state when an interpreter
process dies.

try it with

    $ python rewrite.py

and then in another terminal run

    nc -U path/to/tmp/unix/socket/*save

to save terminal states, and

    nc -U path/tmp/tmp/unix/socket/*save; nc -U path/to/tmp/unix/socket/*restore;

to restore previous terminal states. Restore always goes back two state, so it
is necessary to call save before restore as shown above to restore the previous
save. Ordinarily these signals are sent by the modified interpreter (or the
patched readline it calls) after printing the prompt but before the user types
anything. Since you'll be sending the commands manually in the above demo, the
`>` prompt will not reappear after undo.

#Running the tests

* clone the repo, create a virtual environment
* pip install nose
* install [tmux](https://github.com/tmux/tmux) 1.9a or 2.1 or later. 1.8 is
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
* Madelyn Freed for work on the executable rlundo script

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

---

    $ python rlundo ipython

![undo with ctrl+c](http://ballingt.com/assets/undoable_ipython.gif)
