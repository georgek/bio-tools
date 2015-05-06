#!/usr/bin/env python

import sys
import os.path
import argparse
import re

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Prints fasta containing only the given set of sequences.")
parser.add_argument("fasta_file", type=str, help="FASTA file.")
parser.add_argument("regex", type=str, help="Regular expression.")
parser.add_argument("-v", "--invert-match", dest="invert", action="store_true",
                    help="Invert the sense of matching, to select non-matching sequences.")
parser.set_defaults(invert=False)

args = parser.parse_args()
# ----- end command line parsing -----

fasta_file = open(args.fasta_file)
regex = re.compile(args.regex)

printing = False
for line in fasta_file:
    if line[0] == '>':
        if bool(re.search(regex, line[1:-1])) ^ bool(args.invert):
            printing = True
            sys.stdout.write(line)
        else:
            printing = False
    elif printing:
        sys.stdout.write(line)

