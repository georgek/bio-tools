#!/usr/bin/env python

import sys
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(description="Splits contigs in fasta by removing Ns.")
parser.add_argument("file", type=str, help="Fasta file.")

args = parser.parse_args()
# ----- end command line parsing -----

fasta = open(args.file)
names = []
sequences = {}
current = ""

for line in fasta:
    if line[0] == '>':
        current = line[1:].strip().split()[0]
        names.append(current)
        sequences[current] = ""
    else:
        sequences[current] += line.strip()

for name in names:
    segments = sequences[name].upper().replace('N', ' ').split()
    for segment, n in zip(segments, range(len(segments))):
        sys.stdout.write(">{:s}-{:d}\n".format(name, n))
        sys.stdout.write("{:s}\n".format(segment))

