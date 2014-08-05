#!/usr/bin/env python

# gives average of selected column

import sys
import os.path
import argparse
from collections import namedtuple
import sqlite3

def mean(list):
    return sum(list)/len(list)

def median(list):
    if len(list)%2:
        return sorted(list)[len(list)/2]
    else:
        return (sorted(list)[len(list)/2-1]+sorted(list)[len(list)/2])/2

def mode(list):
    mode = None
    modecount = 0
    current = None
    currentcount = 0
    for item in sorted(list):
        if item == current:
            currentcount += 1
        else:
            if currentcount > modecount:
                mode = current
                modecount = currentcount
            current = item
            currentcount = 1
    return mode if currentcount < modecount else current

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Calculates average (mean, median, or mode) of column.")
parser.add_argument("column_number", type=int, help="The column number.")

parser.add_argument("-d", "--delimiter", default='\t')
parser.add_argument("-f", "--default", type=float, default=0.0)

avg_type = parser.add_mutually_exclusive_group()
avg_type.add_argument("-a", "--mean",
                      action="store_const", dest="avg_type", const="mean",
                      help="Calculate mean.")
avg_type.add_argument("-e", "--median",
                      action="store_const", dest="avg_type", const="median",
                      help="Calculate median.")
avg_type.add_argument("-o", "--mode",
                      action="store_const", dest="avg_type", const="mode",
                      help="Calculate mode.")
parser.set_defaults(avg_type="mean")

args = parser.parse_args()
# ----- end command line parsing -----

dl = args.delimiter.decode("string_escape")
values = []
for line in sys.stdin:
    if len(line) > 1:
        try:
            values.append(float(line[:-1].split(dl)[args.column_number - 1]))
        except IndexError as e:
            values.append(args.default)

if len(values) == 0:
    print 0
elif args.avg_type == "median":
    print median(values)
elif args.avg_type == "mode":
    print mode(values)
else:
    print mean(values)
