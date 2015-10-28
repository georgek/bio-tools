#!/usr/bin/env python

import sys
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Sorts fasta by sequence name.")
parser.add_argument("fasta_file", type=str, help="FASTA file.")

args = parser.parse_args()
# ----- end command line parsing -----

sequences = {}

input_file = open(args.fasta_file)
for line in input_file:
    if line[0] == '>':
        current = line
        sequences[current] = []
    else:
        sequences[current].append(line)

for name in sorted(set(sequences)):
    sys.stdout.write(name)
    for line in sequences[name]:
        sys.stdout.write(line)

