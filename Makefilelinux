all: librlundoable rlundo
librlundoable: rlundoable.c
	gcc -Wall -fPIC -shared -o librlundoable.so rlundoable.c -ldl
rlundo: rlundo.c
	gcc rlundo.c -o rlundo
