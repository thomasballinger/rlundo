$ gcc undoable.c -o undoable
$ ./undoable /usr/bin/irb
irb(main):001:0> a = 1
=> 1
irb(main):002:0> undo
undoing ''
irb(main):001:0> a
NameError: undefined local variable or method `a' for main:Object
