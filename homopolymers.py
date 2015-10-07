#!/usr/bin/env python

# returns positions of homopolymers for each contig

import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(description="Finds positions of homopolyomers.")
parser.add_argument("file", type=str, help="Fasta file.")
parser.add_argument("base", type=str, help="The base to look for.")
parser.add_argument("min_length", type=int, help="Minimum length of homopolymer.")

args = parser.parse_args()
# ----- end command line parsing -----

fasta = open(args.file)

sequences = {}
homopolymers = {}

for line in fasta:
    if line[0] == '>':
        name = line[1:-1]
    elif name in sequences:
        sequences[name] += line[:-1]
    else:
        sequences[name] = line[:-1]
        homopolymers[name] = []

for name,seq in sequences.iteritems():
    run = 0
    pos = 0
    for base in seq:
        pos += 1
        if base.upper() == args.base.upper():
            run += 1
        else:
            run = 0

        if run >= args.min_length:
            homopolymers[name].append(pos-run)
            run -= 1


for name,positions in homopolymers.iteritems():
    for position in positions:
        print "{:s}\t{:d}".format(name, position)
