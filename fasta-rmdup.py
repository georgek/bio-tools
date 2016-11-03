#!/usr/bin/env python

# removes duplicated sequences from fasta file based on names

import sys
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(description="Removes duplicated sequences based on reads.")
parser.add_argument("file", type=str, help="Fasta file.")

args = parser.parse_args()
# ----- end command line parsing -----

fasta = open(args.file)

sequences = {}

for line in fasta:
    if line[0] == '>':
        name = line[1:-1]
        sequences[name] = ""
    else:
        sequences[name] += line.strip()

for name,seq in sequences.iteritems():
    sys.stdout.write(">{:s}\n".format(name))
    sys.stdout.write("{:s}\n".format(seq))

