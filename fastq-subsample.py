#!/usr/bin/env python

import sys
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Subsample a read file to lower coverage and/or read length.")
parser.add_argument("fastq_file", type=str, help="FASTQ file.")
parser.add_argument("divide_coverage", type=int, help="Amount of divide coverage by.")
parser.add_argument("read_length", type=int, help="Length to reduce reads to.")

args = parser.parse_args()
# ----- end command line parsing -----

lines = 0
reads = 0
name = ""
read = ""
qual = ""

input_file = open(args.fastq_file)
for line in input_file:
    if lines == 0:
        name = line[1:-1]
    elif lines == 1:
        read = line[:-1]
        if args.read_length < len(read):
            read = read[:args.read_length]
    elif lines == 3:
        qual = line[:-1]
        if args.read_length < len(qual):
            qual = qual[:args.read_length]
        if reads == 0:
            sys.stdout.write("@{:s}\n{:s}\n+\n{:s}\n".format(name, read, qual))
        reads = (reads + 1) % args.divide_coverage
    lines = (lines + 1) % 4
