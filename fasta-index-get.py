#!/usr/bin/env python3

# gets a sequence from an indexed fasta file

import sys
import argparse
import re
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

def get_args():
    parser = argparse.ArgumentParser(
        description="Gets a sequence from an indexed fasta file.")
    parser.add_argument("fasta_file_name", type=str,
                        help="FASTA file.", metavar="fasta_file")
    parser.add_argument("pattern", type=str,
                        help="Regular expression to match sequence name.")
    parser.add_argument("-v", "--invert_match", dest="invert", action="store_true",
                        help="Invert the sense of matching, to select non-matching sequences.")
    parser.set_defaults(invert=False)

    return parser.parse_args()


def get_seq_from_offset(fasta_file, offset):
    fasta_file.seek(offset)
    seq_lines = []
    for seq_line in fasta_file:
        if seq_line[0] == ">":
            break
        else:
            seq_lines.append(seq_line.strip())
    return "".join(seq_lines)


def get_seqs(fasta_file,
             fasta_index,
             pattern,
             invert=False):
    regex = re.compile(pattern)

    seqs = {}
    for line in fasta_index:
        name, length, offset, linebases, linewidth = line.split()
        length, offset, linebases, linewidth = (
            int(n) for n in [length, offset, linebases, linewidth])
        if bool(re.search(regex, name)) ^ bool(invert):
            seqs[name] = get_seq_from_offset(fasta_file, offset)
    return seqs


def main(fasta_file_name,
         pattern,
         invert=False):
    try:
        fasta_file = open(fasta_file_name)
    except:
        sys.stderr.write(fasta_file_name + " not found.\n")
        sys.exit(1)
    try:
        index_file = open(fasta_file_name + ".fai")
    except:
        sys.stderr.write("Index file for " + fasta_file_name + " not found.\n"
                         "Use samtools faidx " + fasta_file_name + "\n")
        sys.exit(2)
    seqs = get_seqs(fasta_file, index_file, pattern, invert)
    for name, seq in seqs.items():
        sys.stdout.write(">{:s}\n{:s}\n".format(name, seq))


if __name__ == '__main__':
    args = get_args()
    main(**vars(args))
