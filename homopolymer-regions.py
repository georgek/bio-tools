#!/usr/bin/env python

# turns output of homopolymers.py into regions

import sys
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(description="Makes homopolymer regions.")
parser.add_argument("file", type=str, help="Homopolymer file.")
parser.add_argument("length", type=int, help="Length of homopolymers.")

args = parser.parse_args()
# ----- end command line parsing -----

homo_file = open(args.file)

lastcontig = ""
laststart = 0
runstart = 0
runend = 0
for line in homo_file:
    [contig,start] = line.split()
    start = int(start)
    if contig == lastcontig:
        if start == laststart + 1:
            runend += 1
            laststart = start
        else:
            sys.stdout.write("{:s}\t{:d}\t{:d}\t{:d}\n"
                             .format(contig, runend-runstart, runstart, runend))
            laststart = start
            runstart = start
            runend = start + args.length
    else:
        if lastcontig != "":
            sys.stdout.write("{:s}\t{:d}\t{:d}\t{:d}\n"
                             .format(lastcontig, runend-runstart, runstart, runend))
        lastcontig = contig
        runstart = start
        runstart = start
        runend = start + args.length
