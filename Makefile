undoable: undoable.c myreadline.c
	gcc -Wall -fPIC -shared -o mylibreadline.so myreadline.c -ldl
	gcc undoable.c -o undoable
