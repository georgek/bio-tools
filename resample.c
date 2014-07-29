#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
     char *progname;
     unsigned bin_size;

     unsigned nlines = 0;
     double current_x = 0, current_y = 0;
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

     while (!feof(stdin)) {
          scanf("%lf\t%lf\n ", &current_x, &current_y);
          nlines++;
          bin_x *= (double)(nlines-1)/nlines;
          bin_x += current_x/nlines;
          bin_y *= (double)(nlines-1)/nlines;
          bin_y += current_y/nlines;
          if (nlines == bin_size) {
               printf("%f\t%f\n", bin_x, bin_y);
               nlines = 0;
               bin_x = 0;
               bin_y = 0;
          }
     }
     return 0;
}
