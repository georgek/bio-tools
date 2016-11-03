#include <stdlib.h>
#include <stdio.h>
#include <memory.h>

static int *numbers;
static int size = 0;
static int init_size = 1000;
static int max_num = 0;

int main(int argc, char *argv[])
{
     int number, i;

     size = init_size;
     numbers = malloc(sizeof(int) * size);
     for (i = 0; i < size; i++) {
          numbers[i] = 0;
     }

     while (scanf("%d\n", &number) != EOF) {
          if (number >= size) {
               i = size;
               size = number * 2;
               numbers = realloc(numbers, sizeof(int) * size);
               for (; i < size; i++) {
                    numbers[i] = 0;
               }
          }
          if (number > max_num) {
               max_num = number;
          }
          numbers[number]++;
     }

     for (i = 0; i <= max_num; i++) {
          printf("%d\t%d\n", i, numbers[i]);
     }
     return 0;
}
