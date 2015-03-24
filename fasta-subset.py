#!/usr/bin/env python

# gives average of selected column

import sys
import os.path
import argparse
from sets import Set

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Prints fasta containing only the given set of sequences.")
parser.add_argument("fasta_file", type=str, help="FASTA file.")
parser.add_argument("sample_names", type=str, help="Sample names.")
parser.add_argument("-p", "--prefix", dest="prefix", action="store_true",
                    help="Names given are a prefix of the name in the fasta.")
parser.set_defaults(prefix=False)

args = parser.parse_args()
# ----- end command line parsing -----

fasta_file = open(args.fasta_file)
sample_names_file = open(args.sample_names)

sample_names = Set()

for line in sample_names_file:
    sample_names.add(line[:-1])

printing = False
for line in fasta_file:
    if line[0] == '>':
        if args.prefix:
            name = line[1:-1].split()[0]
        else:
            name = line[1:-1]
        if name in sample_names:
            printing = True
            sys.stdout.write(line)
        else:
            printing = False
    elif printing:
        sys.stdout.write(line)

