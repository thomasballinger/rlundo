#define _GNU_SOURCE

#include <stdlib.h>
#include <dlfcn.h>
#include <stdio.h>

char* readline(const char *prompt){

  printf("running our readline\n");

  /*
  char* line = (char*)malloc(sizeof(char)*3);
  *line = 'h';
  *(line + sizeof(char)) = 'i';
  *(line + sizeof(char)*2) = '\0';
  */

  char *(*original_readline)(const char*);
  original_readline = dlsym(RTLD_NEXT, "readline");
  return (*original_readline)(prompt);
}

