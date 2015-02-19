#define _GNU_SOURCE

#include <stdlib.h>
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <wait.h>

char * last_command = "with no command, so exiting";


char* readline(const char *prompt){

  char *(*original_readline)(const char*);
  original_readline = dlsym(RTLD_NEXT, "readline");

  char *value;

  value = (*original_readline)(prompt);
  if(!strcmp(value, "undo")){
    printf("undoing '%s'\n", last_command);
    exit(42);
  }
       pid_t pid = fork();

  if (pid == 0) {
    last_command = value;
    return value;
  } else {
    int status;
    waitpid(pid, &status, 0);
    int exitstatus = WEXITSTATUS(status);

    if(exitstatus == 42){
      return readline(prompt);
    } else {
      exit(exitstatus);
    }
  }
}

