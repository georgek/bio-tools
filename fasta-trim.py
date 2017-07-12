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
parser.add_argument("-s", "--split", dest="split", action="store_true",
                    help="Split contigs (default is to have only one copy of each original contig).")
parser.set_defaults(split=False)

args = parser.parse_args()
# ----- end command line parsing -----

fasta_file = open(args.fasta_file)
trim_file = open(args.trim_file)

beginnings = {}
ends = {}
for line in trim_file:
    name,beg,end = line.split()
    if (args.split):
        if name not in beginnings:
            beginnings[name] = [int(beg)]
        else:
            beginnings[name].append(int(beg))
        if name not in ends:
            ends[name] = [int(end)]
        else:
            ends[name].append(int(end))
    else:
        if name not in beginnings:
            beginnings[name] = [int(beg)]
        else:
            beginnings[name] = [max(int(beg), beginnings[name][0])]
        if name not in ends:
            ends[name] = [int(end)]
        else:
            ends[name] = [min(int(end), ends[name][0])]
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

for name,seq in seqs.items():
    if not args.exclude or name in beginnings:
        nseq = 0
        while len(beginnings[name]) > 0:
            nseq += 1
            seqbeg = beginnings[name].pop()-1 if name in beginnings else 0
            seqend = ends[name].pop() if name in ends else len(seq)
            if (seqbeg < seqend):
                sys.stdout.write(">{:s}_{:d}\n".format(name,nseq))
                sys.stdout.write("".join(seq[seqbeg:seqend]))
                sys.stdout.write("\n")
name = line[1:-1]
seq = []
