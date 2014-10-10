#!/usr/bin/env python

# gives average of selected column

import sys
import os.path
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Prints fasta containing only the given set of sequences.")
parser.add_argument("fasta_file", type=str, help="FASTA file.")
parser.add_argument("sample_names", type=str, help="Sample names.")

args = parser.parse_args()
# ----- end command line parsing -----

fasta_file = open(args.fasta_file)
sample_names_file = open(args.sample_names)

sample_names = []

for line in sample_names_file:
    sample_names.append(line[:-1])

printing = False
for line in fasta_file:
    if line[0] == '>':
        if line[1:-1] in sample_names:
            printing = True
            sys.stdout.write(line)
        else:
            printing = False
    elif printing:
        sys.stdout.write(line)

