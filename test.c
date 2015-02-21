#include<stdlib.h>
#include<stdio.h>

extern char* readline(const char*);

int main(){
   char* line;

   line = readline("enter a string:  ");  // readline allocates space for returned string
   if(line != NULL) { 
       printf("You entered: %s\n", line);
       free(line);   // but you are responsible for freeing the space
   }
}
