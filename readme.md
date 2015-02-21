get undo in any interactive command line tool that uses readline!

    $ gcc undoable.c -o undoable
    $ ./undoable /usr/bin/irb
    irb(main):001:0> a = 1
    => 1
    irb(main):002:0> undo
    undoing ''
    irb(main):001:0> a
    NameError: undefined local variable or method `a' for main:Object



Based on http://wwwold.cs.umd.edu/Library/TRs/CS-TR-4585/CS-TR-4585.pdf I think the more elegant dynamic linking solution won't on osx (I tried for a bit and then read that and decided to give up) so we assume some things about the location of readline.
