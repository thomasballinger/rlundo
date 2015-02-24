get undo in any interactive command line tool that uses readline! (and dynamically links to it in a way this program can intercept)

    $ make -f Makefilelinux
    $ ./undoable /usr/bin/irb
    irb(main):001:0> a = 1
    => 1
    irb(main):002:0> undo
    undoing 'a = 1'
    irb(main):001:0> a
    NameError: undefined local variable or method `a' for main:Object

Use the makefile for your system


OSX support is flaky right now.
Based on http://wwwold.cs.umd.edu/Library/TRs/CS-TR-4585/CS-TR-4585.pdf I think the more elegant dynamic linking solution won't on osx (I tried for a bit and then read that and decided to give up) so we assume some things about the location of readline.

It's currently hardcoded to try to load readline from

    /usr/local/opt/readline/lib/libreadline.6.dylib

which happens to be where brew puts it on my computer.



Works with
* irb

By setting new library path directores, we could get racket to work
