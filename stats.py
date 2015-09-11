#!/usr/bin/env python

# gives average of selected column

import sys
import argparse
import re


def mean(list):
    if len(list) > 0:
        return sum(list)/len(list)
    else:
        return 0


def median(list):
    if len(list) == 0:
        return 0
    elif len(list) % 2:
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


def variance(list):
    lmean = mean(list)
    sqdiffs = map(lambda x: pow(x - lmean, 2), list)
    return mean(sqdiffs)


def stddev(list):
    return pow(variance(list), 0.5)


def N50(list):
    total = sum(list)
    currentsum = 0
    for item in sorted(list):
        currentsum += item
        if currentsum > total/2:
            return item


def formatfloat(number, width, precision, separators,
                defaultwidth, defaultprecision):
    if separators:
        fmt = "{0:{1},.{2}f}"
    else:
        fmt = "{0:{1}.{2}f}"
    return fmt.format(number,
                      width if width else defaultwidth,
                      precision if precision else defaultprecision)


# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Calculates stats for column and prints according to format string.")
parser.add_argument("-c", "--column", type=int,
                    help="The column number.")

parser.add_argument("-f", "--format", type=str,
                    help="Format string.")

parser.add_argument("-d", "--delimiter", default=None,
                    help="Column delmiter.")

parser.add_argument("-t", "--thousand_separators", dest="seps", action="store_true",
                    help="Print numbers with thousand separators.")
parser.set_defaults(seps=False)

parser.add_argument("-p", "--precision", default=2,
                    help="Default precision of floating point numbers.")

parser.add_argument("-w", "--width", default=0,
                    help="Default width of floating point numbers.")

parser.add_argument("--default", type=float, default=0.0,
                    help="Default value for missing values.")

args = parser.parse_args()
# ----- end command line parsing -----

if args.format:
    fmt_str = args.format.decode("string_escape")
else:
    fmt_str = "Mean: %a, median: %e, mode: %o, min: %m, max: %M, stdev: %s\n"

if args.column:
    col = args.column
else:
    col = 1

if args.delimiter:
    dl = args.delimiter.decode("string_escape")
else:
    dl = None
values = []
for line in sys.stdin:
    if len(line) > 1:
        try:
            values.append(float(line[:-1].split(dl)[col - 1]))
        except IndexError as e:
            values.append(args.default)

fmt_re = re.compile("%([0-9]+)?(?:.([0-9]+))?([naeomMvsSN])")
chunks = fmt_re.split(fmt_str)
sys.stdout.write(chunks[0])
i = 1
while i < len(chunks):
    type = chunks[i+2]
    if len(values) == 0:
        val = 0
    elif type == 'n':
        val = len(values)
    elif type == 'a':
        val = mean(values)
    elif type == 'e':
        val = median(values)
    elif type == 'o':
        val = mode(values)
    elif type == 'm':
        val = min(values)
    elif type == 'M':
        val = max(values)
    elif type == 'v':
        val = variance(values)
    elif type == 's':
        val = stddev(values)
    elif type == 'S':
        val = sum(values)
    elif type == 'N':
        val = N50(values)
    else:
        sys.stderr.write("Unrecognised type {:s}.".format(type))
    sys.stdout.write(formatfloat(val, chunks[i], chunks[i+1], args.seps,
                                 args.width, args.precision))
    sys.stdout.write(chunks[i+3])
    i += 4
