#rlundo

Adds undo to interactive command line programs that use readline.
Undo is implemented by forking the process every time readline()
is called to save previous states, and returning to these saved
states by exiting the child process which continued execution of
the program if "undo" is entered.

I'm trying out two different techniques for modifying readline: function interposition
and patching readline.
I'm also trying to figure out how how to get an executable to load the modified
readline function instead of the system one.


##Recipes

irb (interactive Ruby interpreter)
----------------------------------

I can get `irb` to work on linux and OSX with 

    $ make -f Makefilelinux rlundo
    $ ./rlundo /usr/bin/irb
    irb(main):001:0> a = 1
    => 1
    irb(main):002:0> undo
    undoing 'a = 1'
    irb(main):001:0> a
    NameError: undefined local variable or method `a' for main:Object

racket
------

Racket is working for me on linux, but not osx where weird things seem to happen.

    $ make -f Makefilelinux rlundopatched
    gcc rlundopatched.c -o rlundopatched
    echo '(require readline)' > ~/.racketrc
    $ ./rlundopatched /usr/bin/racket -il readline
    Welcome to Racket v5.3.6.
    > (define a 1)
    > undo
    undoing '(define a 1)'
    > a
    a: undefined;
    cannot reference undefined identifier
    context...:
    /usr/share/racket/collects/racket/private/misc.rkt:87:7

Racket bugs:
* there seems to be an extra readline call that happens at startup?
* doesn't exit cleanly

##Techniques for creating the substitute readline function

###Proxying readline calls to your system readline (function interposition)

rlundoable.c contains a function called readline which when called by a program with
find your call out to the readline function the program would have used.

`irb` is known to work with this technique on linux and OSX.

    $ make -f Makefilelinux rlundo
    $ ./rlundo ./test.out
    enter a string: undo
    undoing 'with no command, so exiting'

OSX support for this is flaky right now.
Based on http://wwwold.cs.umd.edu/Library/TRs/CS-TR-4585/CS-TR-4585.pdf
I think the more elegant solution of dynamically locating the
original readline with (`dlsym(RTLD_NEXT, "readline")`) won't work
(I tried for a bit and then read that and decided to give up)
so we assume some things about the location of readline.

It's currently hardcoded to try to load readline from

    /usr/local/opt/readline/lib/libreadline.6.dylib

which happens to be where brew puts it on my computer.

###Using a patched readline library

Instead of proxying calls between a program and the real readline library,
we can download the real readline library and patch it with out undo behavior.


    $ make -f Makefileosx libreadline.6.3.dylib
    ... (lots of compiling output)
    $ make -f Makefileosx libedit.3.dylib
    ln -s libreadline.6.3.dylib libedit.3.dylib
    $ DYLD_LIBRARY_PATH=. ./test.out
    enter a string: undo
    undoing 'with no command, so exiting'

##Techniques for getting programs to load our readline function
=============================================================

###LD_PRELOAD

LD_PRELOAD is the method I've found referenced most often: add the name of
a dynamic library (`lib*.so` or `lib*.dylib`) to an environmental variable
that causing that file to be loaded before any others.

rlundo uses this technique, but you can also test it by setting these environmental
variables directly:

linux: 

  $ LD_PRELOAD=./librlundoable.dylib ./test.out

osx:

  $ DYLD_FORCE_FLAT_NAMESPACE=1 DYLD_INSERT_LIBRARIES=./librlundoable.dylib ./test.out

This seems to works for things 


###Library Path

Some programs seem to implement loading behavior themselves and don't respect LD_PRELOAD.
rlundolibpath runs programs in an environment with LD_LIBRARY_PATH set to the current directory,
but you can also try this directly:

    $ rlundolibpath ./test.out
    $ LD_LIBRARY_PATH=. ./test.out

For this to work, the name of the dynamic library needs to be the same as the one linked against,
hence the aliasing in the makefile:

    $ make -f Makefileosx libedit.3.dylib
    ln -s libreadline.6.3.dylib libedit.3.dylib
    $ DYLD_LIBRARY_PATH=. ./test.out

racket seems to work with this approach (but right now is segfaulting)



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
