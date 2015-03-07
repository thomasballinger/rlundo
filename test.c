/*
 * A simple program that uses readline.
 *
 * To use this to test, somehow get this executable to load
 * the rlundoable.so/rlundoable.so instead of normal readline.
 * like LD_PRELOAD for linux
 * or DLYD_INSERT_LIBRARIES and DYLD_FORCE_FLAT_NAMESPACE on osx
 * Then type "undo" 
*/

#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include<readline/readline.h>
#include<readline/history.h>
#include<dlfcn.h>


int main(){
   printf("starting main\n");
   char* line;

   //char *(*original_readline)(const char*) = NULL;
   //original_readline = dlsym(RTLD_NEXT, "readline");
   //printf("here's the original_readline: %d\n", (int)original_readline);

   printf("about to call readline\n");
   const char* prompt = "enter a string: ";
   line = readline(prompt);  // readline allocates space for returned string
   printf("done calling readline\n");
   if(line != NULL) { 
       printf("You entered: %s\n", line);
       if(!strcmp(line, "undo")){
         printf("looks like we're using normal readline\n");
       }
       free(line);   // but you are responsible for freeing the space
   }
}
