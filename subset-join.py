#!/usr/bin/env python

# for doing a join on files that you know are sorted the same way and one is a
# subset of the other

import sys
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Does a join on column 1 for files where one is a subset of the other and the"
    "are sorted the same way.")

parser.add_argument("big_file", type=str,
                    help="Big file (superset).")
parser.add_argument("little_file", type=str,
                    help="Little file (subset).")

args = parser.parse_args()
# ----- end command line parsing -----

big = open(args.big_file)
little = open(args.little_file)

for little_line in little:
    little_split = little_line.split()
    for big_line in big:
        big_split = big_line.split()
        if big_split[0] == little_split[0]:
            sys.stdout.write("{:s}\t{:s}\t{:s}\n".format(big_split[0],
                                                         "\t".join(big_split[1:]),
                                                         "\t".join(little_split[1:])))
            break
