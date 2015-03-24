To test, try

    $ DYLD_LIBRARY_PATH=modified-readline-6.3/shlib ./test.out

or

    $ DYLD_LIBRARY_PATH=modified-readline-6.3/shlib /usr/bin/irb



#Implementation Notes

Adds undo to interactive command line programs that use readline.
Undo is implemented by forking the process every time readline()
is called to save previous states, and returning to these saved
states by exiting the child process which continued execution of
the program if "undo" is entered.

I'm trying out two different techniques for modifying readline: function interposition
and patching readline.
I'm also trying to figure out how how to get an executable to load the modified
readline function instead of the system one.

    $ ./rlundo /usr/bin/irb
    $ ./rlundopatched /usr/bin/racket -il readline
    $ ./rlundo /usr/bin/lua

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
* not quite working on osx - racket crashes in many cases

lua
---

lua works either way on linux:

    $ make -f Makefilelinx rlundo
    $ ./rlundo /usr/bin/lua
    Lua 5.2.3  Copyright (C) 1994-2013 Lua.org, PUC-Rio
    > a = 1
    > undo
    undoing 'a = 1'
    > print(a)
    nil

but on osx it requires changing the library path:

    $ make -f Makefileosx rlundolibpath patched-readline
    $ cd modified-libreadline-6.3/shlib
    $ ./rlundo /usr/bin/lua
    Lua 5.2.3  Copyright (C) 1994-2013 Lua.org, PUC-Rio

python
------

Python and IPython don't work yet! The readline linking story seems more
complicated. I'd appreciate help with this!

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
so we assume an exact location for the readline library.

It's currently hardcoded to try to load readline from

    /usr/local/opt/readline/lib/libreadline.6.dylib

which happens to be where brew puts it on my computer.

###Using a patched readline library

Instead of proxying calls between a program and the real readline library,
we can download the real readline library and patch it with our undo behavior.

    $ make -f Makefileosx libreadline.6.3.dylib
    ... (lots of compiling output)
    $ make -f Makefileosx libedit.3.dylib
    ln -s libreadline.6.3.dylib libedit.3.dylib
    $ DYLD_LIBRARY_PATH=. ./test.out
    enter a string: undo
    undoing 'with no command, so exiting'

##Techniques for getting programs to load our readline function

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

racket seems to work with this approach (but right now is segfaulting on osx)
