#!/usr/bin/env python

# gets a sequence from an indexed fasta file

import sys
import argparse
import re

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Gets a sequence from an indexed fasta file.")
parser.add_argument("fasta_file", type=str, help="FASTA file.")
parser.add_argument("regex", type=str, help="Regular expression to match sequence name.")
parser.add_argument("-v", "--invert-match", dest="invert", action="store_true",
                    help="Invert the sense of matching, to select non-matching sequences.")
parser.set_defaults(invert=False)

args = parser.parse_args()
# ----- end command line parsing -----

try:
    fasta_file = open(args.fasta_file)
except:
    sys.stderr.write(args.fasta_file + " not found.\n")
    exit()
try:
    index_file = open(args.fasta_file + ".fai")
except:
    sys.stderr.write("Index file for " + args.fasta_file + " not found.\n"
                     "Use samtools faidx " + args.fasta_file + "\n")
    exit()

regex = re.compile(args.regex)

for line in index_file:
    [name, length, offset, linebases, linewidth] = line.split()
    [length, offset, linebases, linewidth] = [int(n) for n in [length, offset, linebases, linewidth]]
    if bool(re.search(regex, name)) ^ bool(args.invert):
        sys.stdout.write(">{:s}\n".format(name))
        fasta_file.seek(offset)
        for seq_line in fasta_file:
            if seq_line[0] == ">":
                break
            else:
                sys.stdout.write(seq_line)
