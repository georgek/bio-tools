#!/usr/bin/env python

# replaces column(s) with ascii bars

import sys
import argparse

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    prog="bars",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Turns some columns into ASCII bars.")
parser.add_argument("column", type=int,
                    help="Column to use for bars.")
parser.add_argument("-d", "--delimiter", type=str,
                    help="Column delimeter.")

args = parser.parse_args()
# ----- end command line parsing -----

lines = []
lengths = []
bars = []
for line in sys.stdin:
    lines.append(line[:-1])
    lengths.append(len(line)-1)
    bars.append(float(line.split(args.delimiter)[args.column-1]))

mbar = max(bars)
mlen = max(lengths)
for line, bar in zip(lines, bars):
    sys.stdout.write(line.ljust(mlen) + " ")
    sys.stdout.write("*" * int(bar/mbar * 10) + "\n")
