#!/usr/bin/env python

import sys
import os.path
import argparse

def open_output_file(output_dir, input_name, number, input_ext):
    n_string = "{:03d}".format(number)
    output_file_name = os.path.join(output_dir, ".".join([input_name, n_string, input_ext]))
    if os.path.isfile(output_file_name):
        raise Exception("File exists: " + output_file_name)
    else:
        output_file = open(output_file_name, "w")
    return output_file

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Splits file into files containing no more than the given number of sequences.")
parser.add_argument("fasta_file", type=str, help="FASTA file.")
parser.add_argument("num_seqs", type=int, help="Maximum sequences per file.")
parser.add_argument("output_dir", type=str, default=".", help="Output directory.")

args = parser.parse_args()
# ----- end command line parsing -----

input_name = args.fasta_file
input_ext = input_name.split(".")[-1]
if input_ext in ["fa", "fas", "fasta", "fsa"]:
    input_name = ".".join(input_name.split(".")[:-1])
else:
    input_ext = "fasta"

input_file = open(args.fasta_file)

output_file_n = 1
outputted_seqs = -1
output_file = None
for line in input_file:
    if line[0] == '>':
        outputted_seqs += 1
        if outputted_seqs % args.num_seqs == 0:
            if output_file:
                output_file.close()
            output_file = open_output_file(args.output_dir, input_name, output_file_n, input_ext)
            output_file_n += 1
    output_file.write(line)
