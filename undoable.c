#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
  // Check that we have at least one arg.
  if (argc == 1) {
    printf("You must supply a program which uses readline to run\n");
    printf("\n");
    printf("Example: %s /bin/irb\n", argv[0]);
    return 1;
  }
  // TODO: allow names without paths

  char **env = malloc(3 * sizeof(char *));
  env[0] = malloc(100 * sizeof(char));
  sprintf(env[0], "LD_PRELOAD=./libreadline.so:/lib/x86_64-linux-gnu/libtinfo.so.5");

  env[1] = NULL;

  execve(argv[1], argv + 1, env);    /* Note that exec() will not return on success. */
  perror("exec() failed");

  free(env[0]);
  free(env);

  return 2;
}
