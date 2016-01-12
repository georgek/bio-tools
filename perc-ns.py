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
        sequences[current] = ""
    else:
        sequences[current] += line

tot = 0
ns = 0
for name,seq in sequences.iteritems():
    tot += len(seq)
    ns += str(seq).lower().count('n')

print "Total: ", tot
print "Ns: ", ns
print "Perc: ", float(ns)/tot
