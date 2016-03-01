#!/usr/bin/env python

# gives average of selected column

import sys
import argparse
import re
import numpy as np

default_fmt_str = r"Mean: %a, median: %e, mode: %o, min: %m, max: %M, stdev: %s\n"

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
    prog="stats",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=
"""Calculates stats from standard input and prints according to format string.

The format  string is  a bit  like a  C format  string. Format  specifiers are
subsequences beginning with % and are replaced with statistics calculated from
the standard input. A format specifier follows this prototype:

%[width][.precision]specifier[{column}]

where the specifier character is one of the following:
    n : number of values,
    a : mean,
    e : median,
    o : mode,
    m : min,
    M : max,
    v : variance,
    s : standard deviation,
    S : sum,
    N : N50.

The width  and precision control the  amount of padding and  number of decimal
places,  respectively.  The  column specifies  which column  of the  input the
statistic is calculated from. By default it is the column given by -c.

The default format string is:
""" + default_fmt_str)
parser.add_argument("-c", "--column", type=int, default=1,
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
    fmt_str = default_fmt_str.decode("string_escape")

if args.delimiter:
    dl = args.delimiter.decode("string_escape")
else:
    dl = None

fmt_re = re.compile("%([0-9]+)?(?:.([0-9]+))?([naeomMvsSN])({[0-9]+})?")
chunks = fmt_re.split(fmt_str)
strs,wdts,decs,typs,cols = [],[],[],[],[]
strs.append(chunks[0])
i=1
while i+4 < len(chunks):
    wdts.append(chunks[i])
    decs.append(chunks[i+1])
    typs.append(chunks[i+2])
    if chunks[i+3] is None:
        cols.append(args.column)
    else:
        cols.append(int(chunks[i+3][1:-1]))
    strs.append(chunks[i+4])
    i += 5
assert len(wdts) == len(decs) == len(typs) == len(cols) == len(strs)-1

ucols = [x-1 for x in list(set(cols))]
locs = {}
for i in range(len(ucols)):
    locs[ucols[i]] = i

try:
    matrix = np.loadtxt(sys.stdin, usecols=ucols, ndmin=2)
except IndexError as e:
    sys.exit("Specified column not available.")
except ValueError as e:
    sys.exit(e)

for i in range(len(wdts)):
    sys.stdout.write(strs[i])
    values = matrix[:,locs[cols[i] - 1]]
    if len(values) == 0:
        val = 0
    elif typs[i] == 'n':
        val = len(values)
    elif typs[i] == 'a':
        val = np.mean(values)
    elif typs[i] == 'e':
        val = np.median(values)
    elif typs[i] == 'o':
        val = mode(values)
    elif typs[i] == 'm':
        val = np.min(values)
    elif typs[i] == 'M':
        val = np.max(values)
    elif typs[i] == 'v':
        val = np.var(values)
    elif typs[i] == 's':
        val = np.std(values)
    elif typs[i] == 'S':
        val = np.sum(values)
    elif typs[i] == 'N':
        val = N50(values)
    else:
        sys.stderr.write("Unrecognised type {:s}.".format(typs[i]))
    sys.stdout.write(formatfloat(val, wdts[i], decs[i], args.seps,
                                 args.width, args.precision))
sys.stdout.write(strs[i+1])
