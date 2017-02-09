#!/usr/bin/env python

import sys
import os.path
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Prints fasta file trimmed according to trim file.")
parser.add_argument("fasta_file", type=str, help="FASTA file.")
parser.add_argument("trim_file", type=str, help="Trim file..")
parser.add_argument("-p", "--prefix", dest="prefix", action="store_true",
                    help="Names given are a prefix of the name in the fasta.")
parser.set_defaults(prefix=False)
parser.add_argument("-e", "--exclude", dest="exclude", action="store_true",
                    help="Exclude names not given in trim file (default is to leave untrimmed).")
parser.set_defaults(exclude=False)

args = parser.parse_args()
# ----- end command line parsing -----

fasta_file = open(args.fasta_file)
trim_file = open(args.trim_file)

beg = {}
end = {}
for line in trim_file:
    split = line.split()
    name = split[0]
    if name not in beg:
        beg[name] = int(split[1])
    else:
        beg[name] = max(int(split[1]), beg[name])
    if name not in end:
        end[name] = int(split[2])
    else:
        end[name] = min(int(split[2]), end[name])
trim_file.close()

seqs = {}
name = ""
seq = []
for line in fasta_file:
    if line[0] == '>':
        if seq:
            seqs[name] = seq
        if args.prefix:
            name = line[1:-1].split()[0]
        else:
            name = line[1:-1]
        seq = []
    else:
        seq = seq + list(line[:-1])
if seq:
    seqs[name] = seq

for name,seq in seqs.iteritems():
    if not args.exclude or name in beg:
        seqbeg = beg[name]-1 if name in beg else 0
        seqend = end[name] if name in end else len(seq)
        if (seqbeg < seqend):
            print ">{:s}".format(name)
            print ''.join(seq[seqbeg:seqend])
name = line[1:-1]
seq = []
