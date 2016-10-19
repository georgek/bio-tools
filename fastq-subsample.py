#!/usr/bin/env python3

import sys
import argparse

block_size = 10000

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Subsample a read file to lower coverage and/or read length.")
parser.add_argument("fastq_file", type=str, help="FASTQ file.")
parser.add_argument("divide_coverage", type=float, help="Amount to divide coverage by.")
parser.add_argument("old_read_length", type=int, help="Length of original reads.")
parser.add_argument("new_read_length", type=int, help="Length to reduce reads to.")

args = parser.parse_args()
# ----- end command line parsing -----

lines = 0
reads = 0
name = ""
read = ""
qual = ""

len_ratio = args.new_read_length/args.old_read_length
cov_ratio = 1/args.divide_coverage/len_ratio
num_reads = int(cov_ratio * block_size)

input_file = open(args.fastq_file)
for line in input_file:
    if lines == 0:
        name = line[1:-1]
    elif lines == 1:
        read = line[:-1]
        if args.new_read_length < len(read):
            read = read[:args.new_read_length]
    elif lines == 3:
        qual = line[:-1]
        if args.new_read_length < len(qual):
            qual = qual[:args.new_read_length]
        if reads < num_reads:
            sys.stdout.write("@{:s}\n{:s}\n+\n{:s}\n".format(name, read, qual))
        reads = (reads + 1) % block_size
    lines = (lines + 1) % 4
