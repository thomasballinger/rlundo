#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
  // Check that we have at least one arg.
  if (argc == 1) {
    printf("You must supply a program which uses readline to run\n");
    printf("\n");
    printf("Example: %s /bin/irb\n", argv[0]);
    system("env");
    return 1;
  }
  // TODO: allow names without paths

  char **env = malloc(3 * sizeof(char *));
  env[0] = malloc(100 * sizeof(char));
#ifdef __APPLE__
  sprintf(env[0], "DYLD_FORCE_FLAT_NAMESPACE=1");
  sprintf(env[1], "DYLD_INSERT_LIBRARIES=./librlundoable.dylib");
  env[2] = NULL;
#else 
  sprintf(env[0], "LD_PRELOAD=./librlundoable.so");
  env[1] = NULL;
#endif

  execve(argv[1], argv + 1, env);    /* Note that exec() will not return on success. */
  perror("exec() failed");

  free(env[0]);
  free(env);

  return 2;
}
