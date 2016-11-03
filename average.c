#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>

int main(int argc, char **argv)
{
     int c;
     enum average {MEAN, MEDIAN, MODE} type = MEAN;

     while (1) {
          static struct option long_options[] = {
               {"mean",     no_argument,       0, 'a'},
               {"median",   no_argument,       0, 'e'},
               {"mode",     no_argument,       0, 'o'},
               {"delimiter",required_argument, 0, 'd'},
               {"default",  required_argument, 0, 'f'},
               {0, 0, 0, 0}
          };
          /* getopt_long stores the option index here. */
          int option_index = 0;

          c = getopt_long(argc, argv, "aeod:f:",
                          long_options, &option_index);

          /* Detect the end of the options. */
          if (c == -1) {
               break;
          }

          switch (c) {
          case 0:
               /* If this option set a flag, do nothing else now. */
               if (long_options[option_index].flag != 0) {
                    break;
               }
               printf("option %s", long_options[option_index].name);
               if (optarg) {
                    printf(" with arg %s", optarg);
               }
               printf("\n");
               break;
          case 'a':
               type = MEAN;
               break;
          case 'e':
               type = MEDIAN;
               break;
          case 'o':
               type = MODE;
               break;
          case 'd':
               printf("delimiter %s\n", optarg);
               break;
          case 'f':
               printf("default %s\n", optarg);
               break;
          case '?':
               /* getopt_long already printed an error message. */
               break;
          default:
               abort();
               break;
          }
     }

     /* print any remaining command line arguments (not options). */
     if (optind < argc) {
          printf("non-option ARGV-elements: ");
          while (optind < argc) {
               printf("%s ", argv[optind++]);
          }
          putchar('\n');
     }

     switch (type) {
     case MEAN:
          printf("mean\n");
          break;
     case MEDIAN:
          printf("median\n");
          break;
     case MODE:
          printf("mode\n");
          break;
     }

     exit (0);
}
