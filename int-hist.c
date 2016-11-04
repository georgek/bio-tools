#include <stdlib.h>
#include <stdio.h>

int maxitem = 1000;
unsigned long *array = NULL;
char *line = NULL;

int main(int argc, char *argv[])
{
     size_t read;
     size_t len = 0;
     unsigned long val, i;

     array = calloc(maxitem + 1, sizeof(unsigned long));
     while ((read = getline(&line, &len, stdin)) != -1) {
          val = strtoul(line, NULL, 10);
          if (val > maxitem) {
               array = realloc(array, sizeof(unsigned long) * val + 1);
               for (i = maxitem + 1; i < val + 1; ++i){
                    array[i] = 0;
               }
               maxitem = val;
          }
          array[val]++;
     }

     for (i = 0; i < maxitem + 1; ++i) {
          printf("%lu\t%lu\n", i, array[i]);
     }
     
     return 0;
}
