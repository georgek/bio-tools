#!/usr/bin/env python

# returns positions of homopolymers for each contig

import sys
import os
import argparse
import threading
import time
from collections import namedtuple

def progress(fp, fs, fin):
    progress = ["-", "\\", "|", "/"]
    prog = 0
    while not fin.isSet():
        if sys.stderr.isatty():
            sys.stderr.write("\r{:3.0f}% {:s}\b".format(
                fp.tell()/float(fs)*100, progress[prog]))
            sys.stderr.flush()
            prog = (prog + 1)%4
            time.sleep(0.1)
        else:
            sys.stderr.write("{:3.0f}% ".format(
                fp.tell()/float(fs)*100))
            time.sleep(5)
    else:
        if sys.stderr.isatty():
            sys.stderr.write("\r100% *")
        sys.stderr.write("\n")
    return


Homopolymer = namedtuple(
    "Homopolymer",
    "contig base length beginning end begflank endflank")

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Finds positions of homopolyomers.")
parser.add_argument("file", type=str,
                    help="Fasta file.")
parser.add_argument("min_length", type=int,
                    help="Minimum length of homopolymer.")
parser.add_argument("-b", "--bases", type=str,
                    help="List of bases to consider, comma separated.")
parser.add_argument("-l", "--flank_length", type=int, default=21,
                    help="Length of flanking sequences.")

args = parser.parse_args()
# ----- end command line parsing -----

fasta_size = os.path.getsize(args.file)
fasta = open(args.file)

if args.bases is not None:
    bases = args.bases.split(",")
else:
    bases = None

sys.stderr.write("Reading {:s}...\n".format(args.file))
fin = threading.Event()
pthread = threading.Thread(name = "progress",
                           target = progress,
                           args = (fasta, fasta_size, fin))

homopolymers = []
name = ""
pos = 0
run = 0
last_base = ""
begflank = " " * args.flank_length
endflank = " " * args.flank_length
try:
    pthread.start()
    for line in fasta:
        if line[0] == '>':
            if run >= args.min_length:
                    homopolymers.append(
                        Homopolymer(name, last_base, run,
                                    pos-run+1, pos,
                                    begflank, endflank))
            name = line[1:-1]
            pos = 0
            run = 0
            last_base = ""
            continue
        for base in line[:-1]:
            pos += 1
            if last_base == "":
                last_base = base
                run = 1
            elif base == last_base:
                run += 1
            else:
                if run >= args.min_length:
                    homopolymers.append(
                        Homopolymer(name, last_base, run,
                                    pos-run, pos-1,
                                    begflank, endflank))
                run = 1
                last_base = base
    if run >= args.min_length:
        homopolymers.append(
            Homopolymer(name, last_base, run,
                        pos-run+1, pos,
                        begflank, endflank))
    fin.set()
    pthread.join()
except KeyboardInterrupt:
    fin.set()
    pthread.join()
    isolate_file.close()
    sys.stderr.write("\n")
    sys.exit(1)
fasta.close()

for homo in homopolymers:
    sys.stdout.write("{:s}\t{:s}\t{:d}\t{:d}\t{:d}\t{:s}\t{:s}\n".format(
        *homo))
