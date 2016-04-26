#!/usr/bin/env python

# gives average of selected column

import sys
import argparse
import re
import numpy as np
from collections import namedtuple

default_fmt_str = r"Mean: %a, median: %e, mode: %o, min: %m, max: %M, stdev: %s\n"
default_fmt_str_group = r"%g\tMean: %a, median: %e, mode: %o, min: %m, max: %M, stdev: %s\n"


def mode(array):
    vals = array.tolist()
    mode = None
    modecount = 0
    current = None
    currentcount = 0
    for item in sorted(vals):
        if item == current:
            currentcount += 1
        else:
            if currentcount > modecount:
                mode = current
                modecount = currentcount
            current = item
            currentcount = 1
    return mode if currentcount < modecount else current


def N50(array):
    vals = array.tolist()
    total = sum(vals)
    currentsum = 0
    for item in sorted(vals):
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


# define available statistics
Stat = namedtuple("Stat", "name function")
stats = {'n': Stat("count", len),
         'a': Stat("mean", np.mean),
         'e': Stat("median", np.median),
         'o': Stat("mode", mode),
         'm': Stat("minimum", np.amin),
         'M': Stat("maximum", np.amax),
         'v': Stat("variance", np.var),
         's': Stat("standard deviation", np.std),
         'S': Stat("sum", np.sum),
         'N': Stat("N50", N50),
         'g': Stat("group name", None)}
statstypes = ''.join(stats.keys())
statshelp = ""
for stat in stats:
    statshelp += "   {:s} : {:s},\n".format(stat, stats[stat].name)
statshelp = statshelp[:-2] + '.\n'

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    prog="stats",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=
    """Calculates stats from an input file, if given, or standard input and prints
according to format string.

The format  string is  a bit  like a  C format  string. Format  specifiers are
subsequences beginning with % and are replaced with statistics calculated from
the standard input. A format specifier follows this prototype:

%[width][.precision]specifier[{column}]

where the specifier character is one of the following:
""" + statshelp + """
The width  and precision control the  amount of padding and  number of decimal
places,  respectively.  The  column specifies  which column  of the  input the
statistic is calculated from. By default it is the column given by -c.

The default format string when -g is not used is:
""" + default_fmt_str + """

and when -g is used::
""" + default_fmt_str_group + """

for grouped (-g).""")
parser.add_argument("file", type=str, nargs='?',
                    help="Input file. If not given, read from standard input.")
parser.add_argument("-c", "--column", type=int, default=1,
                    help="The column number.")
parser.add_argument("-d", "--delimiter", default=None,
                    help="Column delmiter.")
parser.add_argument("--default", type=float, default=0.0,
                    help="Default value for missing values.")

parser.add_argument("-g", "--group_by", default=None, type=int,
                    help="Column to group statistics by.")

parser.add_argument("-f", "--format", type=str,
                    help="Format string.")
parser.add_argument("-t", "--thousand_separators", dest="seps", action="store_true",
                    help="Print numbers with thousand separators.")
parser.set_defaults(seps=False)
parser.add_argument("-p", "--precision", default=2,
                    help="Default precision of floating point numbers.")
parser.add_argument("-w", "--width", default=0,
                    help="Default width of floating point numbers.")

args = parser.parse_args()
# ----- end command line parsing -----

if args.format:
    fmt_str = args.format.decode("string_escape")
elif args.group_by:
    fmt_str = default_fmt_str_group.decode("string_escape")
else:
    fmt_str = default_fmt_str.decode("string_escape")

if args.delimiter:
    dl = args.delimiter.decode("string_escape")
else:
    dl = None

fmt_re = re.compile("%([0-9]+)?(?:.([0-9]+))?([" + statstypes + "])({[0-9]+})?")
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

if args.file is None:
    input_file = sys.stdin
else:
    input_file = open(args.file)

try:
    matrix = np.loadtxt(input_file, usecols=ucols, ndmin=2)
except IndexError as e:
    sys.exit("Specified column not available.")
except ValueError as e:
    sys.exit(e)

if args.group_by:
    input_file.seek(0)
    groupcol = np.loadtxt(input_file, usecols=[args.group_by-1], dtype=object)
    ugroups = np.unique(groupcol)
    indarrays = [np.where(groupcol == group) for group in ugroups]
else:
    ugroups = ["default"]
    indarrays = [np.arange(0,matrix.shape[0])]

for group,indarray in zip(ugroups,indarrays):
    for i in range(len(wdts)):
        sys.stdout.write(strs[i])
        values = matrix[indarray,locs[cols[i] - 1]].flatten()
        if len(values) == 0:
            val = 0
        elif typs[i] == 'g':
            val = group
        elif typs[i] in stats:
            val = stats[typs[i]].function(values)
        else:
            sys.stderr.write("Unrecognised type {:s}.".format(typs[i]))
        if isinstance(val, float):
            sys.stdout.write(formatfloat(val, wdts[i], decs[i], args.seps,
                                         args.width, args.precision))
        elif isinstance(val, str):
            sys.stdout.write(val)
    sys.stdout.write(strs[i+1])
