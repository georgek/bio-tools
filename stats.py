#!/usr/bin/env python

# gives average of selected column

import sys
import os.path
import argparse
import re

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

def formatfloat(number, width, precision):
    return "{0:{1}.{2}f}".format(number,
                                 width if width else 0,
                                 precision if precision else 2)

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Calculates stats for column and prints according to format string.")
parser.add_argument("column_number", type=int, help="The column number.")
parser.add_argument("format_string", type=str, help="Format string.")

parser.add_argument("-d", "--delimiter", default='\t')
parser.add_argument("-f", "--default", type=float, default=0.0)

args = parser.parse_args()
# ----- end command line parsing -----

fmt_str = args.format_string.decode("string_escape")
dl = args.delimiter.decode("string_escape")
values = []
for line in sys.stdin:
    if len(line) > 1:
        try:
            values.append(float(line[:-1].split(dl)[args.column_number - 1]))
        except IndexError as e:
            values.append(args.default)

fmt_re = re.compile("%([0-9]+)?(?:.([0-9]+))?([aeomM])")
chunks = fmt_re.split(fmt_str)
sys.stdout.write(chunks[0])
i = 1
while i < len(chunks):
    type = chunks[i+2]
    if type == 'a':
        val = mean(values)
    elif type == 'e':
        val = median(values)
    elif type == 'o':
        val = mode(values)
    elif type == 'm':
        val = min(values)
    elif type == 'M':
        val = max(values)
    else:
        sys.stderr.write("Unrecognised type {:s}.".format(type))
    sys.stdout.write(formatfloat(val, chunks[i], chunks[i+1]))
    sys.stdout.write(chunks[i+3])
    i += 4
