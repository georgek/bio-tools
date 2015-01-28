#!/usr/bin/env python

import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(description="Prints lengths of contigs in Fasta.")
parser.add_argument("file", type=str, help="Fasta file.")

args = parser.parse_args()
# ----- end command line parsing -----

fasta = open(args.file)

length = None
for line in fasta:
    if line[0] == '>':
        if length:
            print length
        length = 0
    else:
        length += len(line)-1
if length:
    print length
