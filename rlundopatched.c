/*
 * Runs its arguments, in an environment such that a patched
 * version of readline will be used instead of normal readline
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
  // Check that we have at least one arg.
  if (argc == 1) {
    printf("You must supply a program which uses readline to run\n");
    printf("\n");
    printf("Example: %s /bin/irb\n", argv[0]);
    return 1;
  }
  // TODO: allow names without paths

  #ifdef __APPLE__
   WHOOPS not implemented
  #else
    putenv("LD_PRELOAD=./modified-readline-6.3/shlib/libreadline.so.6.3:/lib/x86_64-linux-gnu/libtinfo.so.5");
  #endif

  execv(argv[1], argv + 1);    /* Note that exec() will not return on success. */
  perror("exec() failed");

  return 2;
}
