#!/usr/bin/env python

import sys
import os.path
import argparse
import re

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Prints fasta containing only the given set of sequences.")
parser.add_argument("fasta_file", type=str, help="FASTA file.")
parser.add_argument("prefix", type=str, help="Prefix of names.")

args = parser.parse_args()
# ----- end command line parsing -----

fasta_file = open(args.fasta_file)

printing = False
for line in fasta_file:
    if line[0] == '>':
        if prefix in line[1:-1]:
            printing = True
            sys.stdout.write(line)
        else:
            printing = False
    elif printing:
        sys.stdout.write(line)
