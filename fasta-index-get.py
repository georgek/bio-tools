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

class FaidxEntry:
    def __init__(self, length, offset, linebases, linewidth):
        self.length = int(length)
        self.offset = int(offset)
        self.linebases = int(linebases)
        self.linewidth = int(linewidth)
    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ",".join("{}={!r}".format(k,v) for k,v in self.__dict__.items()))


def index_file_dictionary(index_file):
    index_dict = {}
    for line in index_file:
        name, length, offset, linebases, linewidth = line.split()
        index_dict[name] = FaidxEntry(length, offset, linebases, linewidth)
    return index_dict


def get_seq(fasta_file, faidx_entry, seq_offset=0, seq_length=None):
    """Get the sequence starting from the FaidxEntry from FASTA file with an
optional offset (in sequence positions) and up to a given length (in sequence
length)."""
    extra_offset = ((seq_offset//faidx_entry.linebases)*faidx_entry.linewidth
                    + seq_offset%faidx_entry.linebases)
    fasta_file.seek(faidx_entry.offset + extra_offset)
    if seq_length is None:
        seq_lines = []
        for seq_line in fasta_file:
            if seq_line[0] == ">":
                break
            else:
                seq_lines.append(seq_line.strip())
        return "".join(seq_lines)
    else:
        end_seq_offset = seq_offset + seq_length
        end_offset = ((end_seq_offset//faidx_entry.linebases)*faidx_entry.linewidth
                      + end_seq_offset%faidx_entry.linebases)
        seq = fasta_file.read(end_offset - extra_offset)
        return seq.replace("\n", "").replace("\r", "")


def get_names_and_seqs(fasta_file, fasta_index, pattern, invert=False):
    """Get all names and seqs which match the regular expression pattern."""
    regex = re.compile(pattern)
    for line in fasta_index:
        name, length, offset, linebases, linewidth = line.split()
        if bool(re.search(regex,name)) ^ bool(invert):
            faidx_entry = FaidxEntry(length, offset, linebases, linewidth)
            yield name, get_seq(fasta_file, faidx_entry)


def open_fasta_and_index(fasta_file_name):
    try:
        fasta_file = open(fasta_file_name)
    except OSError:
        sys.stderr.write("Fasta file " + fasta_file_name + " not found.\n")
        raise
    try:
        index_file = open(fasta_file_name + ".fai")
    except OSError:
        sys.stderr.write("Index file for " + fasta_file_name + " not found.\n"
                         "Use samtools faidx " + fasta_file_name + "\n")
        raise
    return fasta_file, index_file


def main(fasta_file_name,
         pattern,
         invert=False):
    try:
        fasta_file, index_file = open_fasta_and_index(fasta_file_name)
    except OSError:
        sys.exit(1)
    for name, seq in get_names_and_seqs(fasta_file, index_file, pattern, invert):
        sys.stdout.write(">{:s}\n{:s}\n".format(name, seq))


if __name__ == '__main__':
    args = get_args()
    main(**vars(args))
