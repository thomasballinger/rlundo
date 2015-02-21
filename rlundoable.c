#define _GNU_SOURCE

#include <stdlib.h>
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#ifdef __APPLE__
  #include <sys/wait.h>
#else 
  #include <wait.h>
#endif

#include<readline/readline.h>
#include<readline/history.h>

static char *top_undo_message = "with no command, so exiting";
static char *last_command;
static char *(*original_readline)(const char*) = NULL;

static char* (*get_original_readline())(const char*){
  char *(*orig_readline)(const char*) = NULL;
  #ifdef __APPLE__
    void* readline_lib = dlopen("/usr/local/opt/readline/lib/libreadline.6.dylib", RTLD_LOCAL);
    if (dlerror()){
      printf("dl error: %s\n", dlerror());
      exit(0);
    }
    orig_readline = dlsym(readline_lib, "readline");
    if (dlerror()){
      printf("dl error: %s\n", dlerror());
      exit(0);
    }
  #else 
    orig_readline = dlsym(RTLD_NEXT, "readline");
  #endif
    return orig_readline;
}

/* Read a line of input.  Prompt with PROMPT.  An empty PROMPT means
   none.  A return value of NULL means that EOF was encountered. */
char* readline(const char *prompt){

  char *value;

  if (!last_command){
    last_command = (char *) malloc(strlen(top_undo_message) + 1);
    strcpy(last_command, top_undo_message);
  }

  if (!original_readline){
    original_readline = get_original_readline();
  }

  value = (*original_readline)(prompt);
  if(!value){
    free(last_command);
    printf("\n");
    exit(0);
  }
  if(!strcmp(value, "undo")){
    printf("undoing '%s'\n", last_command);
    free(last_command);
    exit(42);
  }
   pid_t pid = fork();

  if (pid == 0) { // child
    last_command = strdup(value);
    return value;
  } else { // parent
    int status;
    waitpid(pid, &status, 0);
    int exitstatus = -1;
    if (WIFEXITED(status)){
      exitstatus = WEXITSTATUS(status);
    } else {
      exitstatus = 1; // didn't terminate normally
    }

    if(exitstatus == 42){
      return readline(prompt);
    } else {
      exit(exitstatus);
    }
  }
}

int main(){
   char* line;
   int depth = 0;

   while (1){
     depth++;
     line = readline("enter a string: ");  // readline allocates space for returned string
     if(line != NULL) { 
         printf("You entered: %s\n", line);
         printf("depth: %d\n", depth);
         free(line);   // but you are responsible for freeing the space
     }
   }
}
