#!/usr/bin/env python

import sys
import os
import argparse

def printseq(name, seq):
    sys.stdout.write(">{:s}\n{:s}\n".format(name, seq))


def process_regions(name, seq, regionmap):
    if name not in regionmap:
        return seq
    regions = regionmap[name]
    for (start,end) in regions:
        seq = seq[:start] + "N" * (end-start) + seq[end:]
    return seq

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Replaces given regions with Ns.")
parser.add_argument("fasta", type=str,
                    help="The input fasta file.")
parser.add_argument("regions", type=str,
                    help="The input region file.")

args = parser.parse_args()
# ----- end command line parsing -----

regions = {}

regionfile = open(args.regions)
for line in regionfile:
    [name,length,start,end] = line.split()
    if name not in regions:
        regions[name] = []
    regions[name].append((int(start),int(end)))
regionfile.close()

currentname = None
currentseq = None
fastafile = open(args.fasta)
for line in fastafile:
    if line[0] == ">":
        if currentname:
            newseq = process_regions(currentname, currentseq, regions)
            printseq(currentname, newseq)
        currentname = line.strip()[1:]
        currentseq = ""
    else:
        currentseq += line.strip()
fastafile.close()
if currentname:
    newseq = process_regions(currentname, currentseq, regions)
    printseq(currentname, newseq)
