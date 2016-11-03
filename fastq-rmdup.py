#!/usr/bin/env python3

import sys
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Removes PCR duplicates from reads")

parser.add_argument("R1_input", type=str,
                    help="Input file for R1.")
parser.add_argument("R2_input", type=str,
                    help="Input file for R2.")
parser.add_argument("R1_output", type=str,
                    help="output file for R1.")
parser.add_argument("R2_output", type=str,
                    help="Output file for R2.")

args = parser.parse_args()
# ----- end command line parsing -----

R1in = open(args.R1_input)
R2in = open(args.R2_input)
R1out = open(args.R1_output, 'w')
R2out = open(args.R2_output, 'w')

pairs = set()

nlines = 0
for a,b in zip(R1in, R2in):
    a = a[:-1]
    b = b[:-1]
    if nlines % 4 == 0:
        name1 = a
        name2 = b
    elif nlines % 4 == 1:
        seq1 = a
        seq2 = b
    elif nlines % 4 == 2:
        thing1 = a
        thing2 = b
    elif nlines % 4 == 3:
        qual1 = a
        qual2 = b
        if seq1 + seq2 not in pairs:
            pairs.add(seq1 + seq2)
            R1out.write(name1 + '\n' + seq1 + '\n' + thing1 + '\n' + qual1 + '\n')
            R2out.write(name2 + '\n' + seq2 + '\n' + thing2 + '\n' + qual2 + '\n')
    nlines += 1

print("Duplicates removed: {:d}/{:d} ({:f}%).".format(nlines//4-len(pairs),
                                                      nlines//4,
                                                      ((nlines/4-len(pairs))/(nlines/4))*100))
