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


def get_next_seq(fasta_file,
                 fasta_index,
                 regex,
                 invert=False):
    """Get next matching sequence in the index file, or None. This function
continues to read from the current read pointer of fasta_index and as a side
effect advances the read pointer past the matching sequence. Thus continually
calling this function until it returns None will find every matching
sequence."""
    for line in fasta_index:
        name, length, offset, linebases, linewidth = line.split()
        if bool(re.search(regex, name)) ^ bool(invert):
            faidx_entry = FaidxEntry(length, offset, linebases, linewidth)
            return name, get_seq(fasta_file, faidx_entry)
    else:
        return None,None


def get_seqs(fasta_file,
             fasta_index,
             pattern,
             invert=False):
    """Get a dictionary of all matching sequences in the fasta_index (starting
from the current read pointer)."""
    regex = re.compile(pattern)
    seqs = {}
    while True:
        name, seq = get_next_seq(fasta_file, fasta_index, regex, invert)
        if name is not None:
            seqs[name] = seq
        else:
            break
    return seqs


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
    regex = re.compile(pattern)
    while True:
        name, seq = get_next_seq(fasta_file, index_file, regex, invert)
        if name is not None:
            sys.stdout.write(">{:s}\n{:s}\n".format(name, seq))
        else:
            break


if __name__ == '__main__':
    args = get_args()
    main(**vars(args))
