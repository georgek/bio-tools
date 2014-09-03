#!/usr/bin/env python

# reads a sam file sorted by name and outputs paired fastq files
# pipe in a sam file, e.g. samtools view aln.bam

import sys
import os.path
import argparse

def fastq(name, seq, qual):
    return "@{:s}\n{:s}\n+\n{:s}\n".format(name, seq, qual)

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Make paired fastq files from sam sorted by name.")
parser.add_argument("output_prefix", type=str, help="Prefix for output filenames")

args = parser.parse_args()
# ----- end command linr parsing -----

out1 = open(args.output_prefix + "_1.fastq", "w")
out2 = open(args.output_prefix + "_2.fastq", "w")

read1 = None
read2 = None

for read in sys.stdin:
    if read1 == None:
        read1 = read
        continue

    read2 = read
    split1 = read1.split()
    split2 = read2.split()
    if split1[0] == split2[0]:
        if int(split1[1]) & 0x40:
            out1.write(fastq(split1[0], split1[9], split1[10]))
            out2.write(fastq(split2[0], split2[9], split2[10]))
        else:
            out1.write(fastq(split2[0], split2[9], split2[10]))
            out2.write(fastq(split1[0], split1[9], split1[10]))
    else:
        read1 = read2
        read2 = None

out1.close()
out2.close()
