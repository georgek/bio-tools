#!/usr/bin/env python

import sys
import os.path
import argparse
import threading
import time

def progress(fp, fs, fin, err):
    progress = ["-", "\\", "|", "/"]
    prog = 0
    if (fs <= 0):
        return
    while not fin.isSet() and not err.isSet():
        if sys.stderr.isatty():
            sys.stderr.write("\r{:3.0f}% {:s}\b"
                             .format(fp.tell()/float(fs)*100,
                                     progress[prog]))
            sys.stderr.flush()
            prog = (prog + 1)%4
            time.sleep(0.1)
        else:
            sys.stderr.write("{:3.0f}% "
                             .format(fp.tell()/float(fs)*100))
            time.sleep(5)
    else:
        if sys.stderr.isatty() and fin.isSet():
            sys.stderr.write("\r100% *")
        sys.stderr.write("\n")
    return

def open_output_file(output_dir, input_name, number, input_ext):
    n_string = "{:04d}".format(number)
    output_file_name = os.path.join(output_dir, "."
                                    .join([input_name, n_string, input_ext]))
    if os.path.isfile(output_file_name):
        raise Exception("file exists: " + output_file_name)
    else:
        output_file = open(output_file_name, "w")
    return output_file

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Splits file into files containing no "
    "more than the given number of sequences.")
parser.add_argument("fasta_file", type=str,
                    help="FASTA file.")
parser.add_argument("num_seqs", type=int,
                    help="Maximum sequences per file.")
parser.add_argument("output_dir", type=str, default=".",
                    help="Output directory.")

args = parser.parse_args()
# ----- end command line parsing -----

input_name = args.fasta_file
input_ext = input_name.split(".")[-1]
if input_ext in ["fa", "fas", "fasta", "fsa"]:
    input_name = ".".join(input_name.split(".")[:-1])
else:
    input_ext = "fasta"

fasta_size = os.path.getsize(args.fasta_file)
fasta = open(args.fasta_file)

sys.stderr.write("Reading {:s}...\n".format(args.fasta_file))
fin = threading.Event()
err = threading.Event()
pthread = threading.Thread(name = "progress",
                           target = progress,
                           args = (fasta, fasta_size, fin, err))

output_file_n = 1
outputted_seqs = -1
output_file = None
try:
    pthread.start()
    for line in fasta:
        if line[0] == '>':
            outputted_seqs += 1
            if outputted_seqs % args.num_seqs == 0:
                if output_file:
                    output_file.close()
                output_file = open_output_file(args.output_dir, input_name,
                                               output_file_n, input_ext)
                output_file_n += 1
        output_file.write(line)
    fin.set()
except Exception as e:
    sys.stderr.write("\nError: {:s}".format(e))
    err.set()
except:
    err.set()
pthread.join()
fasta.close()
if output_file:
    output_file.close()
