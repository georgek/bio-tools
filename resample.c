#include <stdlib.h>
#include <stdio.h>

typedef enum{X,SEP,Y,EOL} State;

static inline int numberp(char c)
{
     return c >= '0' && c <= '9';
}

int main(int argc, char *argv[])
{
     char *progname;
     unsigned bin_size;
     char c;

     State state = X;
     unsigned nlines = 0;
     long current_x = 0, current_y = 0;
     double bin_x = 0, bin_y = 0;

     progname = *argv;
     argv++; argc--;
     if (argc < 1) {
          printf("Usage: %s bin_size\n", progname);
          exit(1);
     }
     else {
          bin_size = strtoul(argv[0], NULL, 10);
     }

     while ((c = getc(stdin)) != EOF) {
          switch (state) {
          case X:
               if (numberp(c)) {
                    current_x *= 10;
                    current_x += c & 0xF;
                    break;
               }
               state = SEP;
               break;
          case SEP:
               if (numberp(c)) {
                    state = Y;
               }
               else {
                    break;
               }
          case Y:
               if (numberp(c)) {
                    current_y *= 10;
                    current_y += c & 0xF;
                    break;
               }
               state = EOL;
          case EOL:
               if ('\n' == c) {
                    nlines++;
                    state = X;
                    /* bin_x += current_x; */
                    bin_x *= (double)(nlines-1)/nlines;
                    bin_x += (double)current_x/nlines;
                    current_x = 0;
                    /* bin_y += current_y; */
                    bin_y *= (double)(nlines-1)/nlines;
                    bin_y += (double)current_y/nlines;
                    current_y = 0;
               }
               if (nlines == bin_size) {
                    printf("%f\t%f\n", bin_x, bin_y);
                    nlines = 0;
                    bin_x = 0;
                    bin_y = 0;
               }
          default:
               break;
          }
     }
     return 0;
}
