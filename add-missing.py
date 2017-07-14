#!/usr/bin/env python3

import sys
import argparse
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

def pos_int(val):
    ival = int(val)
    if ival <= 0:
        raise argparse.ArgumentTypeError("requires a positive integer")
    return ival

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Adds missing values in a sequential column.")
parser.add_argument("input", type=str, default=sys.stdin, nargs="?",
                    help="Input file.")
parser.add_argument("-n", "--numcols", type=pos_int, default=1,
                    help="Number of columns in file.")
parser.add_argument("-c", "--column", type=pos_int, default=1,
                    help="Number of column to make sequential.")
parser.add_argument("-d", "--delimiter", type=str, default=None,
                    help="Column delimiter.")
parser.add_argument("-v", "--starting_value", type=int, default=1,
                    help="Starting value of sequential column.")
parser.add_argument("-e", "--empty", type=str, default="-",
                    help="Replace missing fields with EMPTY.")

# ----- end command line parsing -----

def main():
    args = parser.parse_args()

    if args.delimiter is None:
        out_delimiter = " "
    else:
        out_delimiter = args.delimiter

    expected = args.starting_value
    bcols = out_delimiter.join([args.empty]*(args.column-1) + [""])
    acols = out_delimiter.join([""] + [args.empty]*(args.numcols-args.column))

    for line in args.input:
        cols = line.split(args.delimiter)
        found = int(cols[args.column-1])
        if found > expected:
            for x in range(expected, found):
                sys.stdout.write(bcols)
                sys.stdout.write(str(x))
                sys.stdout.write(acols)
                sys.stdout.write("\n")
            expected = found
        sys.stdout.write(line)
        expected += 1

if __name__ == '__main__':
    main()
