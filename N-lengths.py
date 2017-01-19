#!/usr/bin/env python

import sys
import os
import argparse
import re
import threading
import time

def progress(fp, fs, fin):
    progress = ["-", "\\", "|", "/"]
    prog = 0
    while not fin.isSet():
        if sys.stderr.isatty():
            sys.stderr.write("\r{:3.0f}% {:s}\b".format(fp.tell()/float(fs)*100,
                                                        progress[prog]))
            sys.stderr.flush()
            prog = (prog + 1)%4
            time.sleep(0.1)
        else:
            sys.stderr.write("{:3.0f}% ".format(fp.tell()/float(fs)*100))
            time.sleep(5)
    else:
        if sys.stderr.isatty():
            sys.stderr.write("\r100% *")
        sys.stderr.write("\n")
    return


def N_lengths(seq):
    N_lengths = re.split("[^N]+", seq.upper())
    lengths = [len(length) for length in N_lengths]
    if lengths[0] == 0:
        lengths = lengths[1:]
    if lengths[-1] == 0:
        lengths = lengths[:-1]
    return lengths

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Counts lengths of N sequences.")
parser.add_argument("fasta_file", type=str, help="Fasta file.")

args = parser.parse_args()
# ----- end command line parsing -----

sequence = ""
lengths = {}

input_file_size = os.path.getsize(args.fasta_file)
input_file = open(args.fasta_file)

sys.stderr.write("Reading {:s}...\n".format(args.fasta_file))
fin = threading.Event()
pthread = threading.Thread(name = "progress",
                           target = progress,
                           args = (input_file, input_file_size, fin))
try:
    pthread.start()
    for line in input_file:
        if line[0] == ">":
            if sequence != "":
                for length in N_lengths(sequence):
                    if length in lengths:
                        lengths[length] += 1
                    else:
                        lengths[length] = 1
            sequence = ""
        else:
            sequence += line.strip()
    fin.set()
    pthread.join()
except KeyboardInterrupt:
    fin.set()
    pthread.join()
    isolate_file.close()
    sys.stderr.write("\n")
    sys.exit(1)
input_file.close()
        
for length,count in lengths.iteritems():
    sys.stdout.write("{:d}\t{:d}\n".format(length, count))
