#!/usr/bin/env python

# gives average of selected column

import sys
import argparse
import re
import numpy as np
from collections import namedtuple
import warnings

DEFAULT_FMT_STR \
    = "Mean: %a, median: %e, mode: %o, min: %m, max: %M, stdev: %s\\n"
DEFAULT_FMT_STR_GROUP \
    = "%g\\tMean: %a, median: %e, mode: %o, min: %m, max: %M, stdev: %s\\n"
DEFAULT_COLUMN = 1
DEFAULT_DELIMITER = None
DEFAULT_DEFAULT = 0.0
DEFAULT_GROUP_BY = None
DEFAULT_FORMAT = None
DEFAULT_SEPS = False
DEFAULT_PRECISION = 2
DEFAULT_WIDTH = 1


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


def gmean(array):
    return np.exp(np.mean(np.log(array)))


def N50(array):
    vals = array.tolist()
    total = sum(vals)
    if total == 0:
        return 0.0
    currentsum = 0
    for item in sorted(vals):
        currentsum += item
        if currentsum > total/2:
            return item


def nrows(matrix):
    return matrix.shape[0]


Stat = namedtuple("Stat", ["name", "function"])
STATS = {'n': Stat("count", nrows),
         'a': Stat("arithmetic mean", np.mean),
         'h': Stat("geometric mean", gmean),
         'e': Stat("median", np.median),
         'o': Stat("mode", mode),
         'm': Stat("minimum", np.amin),
         'M': Stat("maximum", np.amax),
         'v': Stat("variance", np.var),
         's': Stat("standard deviation", np.std),
         'S': Stat("sum", np.sum),
         'N': Stat("N50", N50),
         'g': Stat("group name", None)}


def stats_help(stats):
    """Return help string for given stats dictionary."""
    statshelp = ""
    for stat in stats:
        statshelp += "   {:s} : {:s},\n".format(stat, stats[stat].name)
    statshelp = statshelp[:-2] + '.\n'
    return statshelp


def stats_regexp(stats):
    """Returns string for use in regular expression to match any stats type."""
    return ''.join(stats.keys())


def parse_args():
    parser = argparse.ArgumentParser(
        prog="stats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"""
Calculates stats from an input file, if given, or standard input and prints
according to format string.

The format string is a bit like a C format string. Format specifiers are
subsequences beginning with % and are replaced with statistics calculated from
the standard input. A format specifier follows this prototype:

%[width][.precision]specifier[{{column}}]

where the specifier character is one of the following:

{stats_help(STATS)}

The width and precision control the amount of padding and number of decimal
places, respectively.  The column specifies which column of the input the
statistic is calculated from. By default it is the column given by -c.

The default format string when -g is not used is:
{DEFAULT_FMT_STR}

and when -g is used:
{DEFAULT_FMT_STR_GROUP}"""
    )
    parser.add_argument("input_file_name", type=str, nargs='?',
                        help="Input file. If not given, "
                        "read from standard input.")
    parser.add_argument("-c", "--column", type=int,
                        default=DEFAULT_COLUMN,
                        help="The column number.")
    parser.add_argument("-d", "--delimiter", type=str,
                        default=DEFAULT_DELIMITER,
                        help="Column delmiter.")
    parser.add_argument("--default", type=float,
                        default=DEFAULT_DEFAULT,
                        help="Default value for missing values.")
    parser.add_argument("-g", "--group_by",
                        default=DEFAULT_GROUP_BY, type=int,
                        help="Column to group statistics by "
                        "(not compatible with reading from stdin).")
    parser.add_argument("-f", "--format_str",
                        default=DEFAULT_FORMAT, type=str,
                        help="Format string.")
    parser.add_argument("-t", "--thousand_separators",
                        dest="seps",
                        action="store_true",
                        help="Print numbers with thousand separators.")
    parser.set_defaults(seps=DEFAULT_SEPS)
    parser.add_argument("-p", "--precision", default=DEFAULT_PRECISION,
                        help="Default precision of floating point numbers.")
    parser.add_argument("-w", "--width", default=DEFAULT_WIDTH,
                        help="Default width of floating point numbers.")

    args = parser.parse_args()
    return args, parser.format_usage()


def formatfloat(number, width, precision, separators,
                defaultwidth, defaultprecision):
    if separators:
        fmt = "{0:{1},.{2}f}"
    else:
        fmt = "{0:{1}.{2}f}"
    return fmt.format(number,
                      width if width else defaultwidth,
                      precision if precision else defaultprecision)


def formatint(number, width, separators, defaultwidth):
    if separators:
        fmt = "{0:{1},d}"
    else:
        fmt = "{0:{1}d}"
    return fmt.format(number,
                      width if width else defaultwidth)


def formatstr(string, width, defaultwidth):
    fmt = "{0:{1}s}"
    return fmt.format(string,
                      width if width else defaultwidth)


def main(input_file_name,
         column=DEFAULT_COLUMN,
         delimiter=DEFAULT_DELIMITER,
         default=DEFAULT_DEFAULT,
         group_by=DEFAULT_GROUP_BY,
         format_str=DEFAULT_FORMAT,
         seps=DEFAULT_SEPS,
         precision=DEFAULT_PRECISION,
         width=DEFAULT_WIDTH):

    if (input_file_name is None or input_file_name == "-") \
       and group_by is not None:
        sys.exit("Can't use groups when reading from standard input.")

    if format_str is None:
        if group_by:
            format_str = DEFAULT_FMT_STR_GROUP
        else:
            format_str = DEFAULT_FMT_STR

    format_str = bytes(format_str, "utf-8").decode("unicode_escape")

    if delimiter:
        dl = bytes(delimiter, "utf-8").decode("unicode_escape")
    else:
        dl = None

    # get bits of format string as chunks. The chunks will contain the
    # important parts of the format string interleaved like so: string, width,
    # decimal, type, column, string, width... where "string" is the bit
    # between any statistic
    fmt_re = re.compile("%([0-9]+)?(?:.([0-9]+))?(["
                        + stats_regexp(STATS)
                        + "])({[0-9]+})?")
    chunks = fmt_re.split(format_str)
    strs, wdts, decs, typs, cols = [], [], [], [], []
    strs.append(chunks.pop(0))
    # deinterleave the rest using five iterators
    for wdt, dec, typ, col, st in zip(*[iter(chunks)]*5):
        wdts.append(wdt)
        decs.append(dec)
        typs.append(typ)
        if typ == "g":
            cols.append(None)
        elif col is None:
            cols.append(column)
        else:
            cols.append(int(col[1:-1]))
        strs.append(st)
    assert len(wdts) == len(decs) == len(typs) == len(cols) == len(strs)-1

    ucols = [x-1 for x in list(set(cols)) if x is not None]
    locs = {}
    for i, ucol in enumerate(ucols):
        locs[ucol] = i

    if input_file_name is None or input_file_name == "-":
        input_file = sys.stdin
    else:
        input_file = open(input_file_name)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            matrix = np.loadtxt(input_file, usecols=ucols,
                                ndmin=2, delimiter=dl)
    except IndexError as e:
        sys.exit("Specified column not available.")
    except ValueError as e:
        sys.exit(e)

    if group_by:
        input_file.seek(0)
        groupcol = np.loadtxt(input_file,
                              usecols=[group_by-1],
                              dtype=object)
        ugroups = np.unique(groupcol)
        indarrays = [np.where(groupcol == group) for group in ugroups]
    else:
        ugroups = ["default"]
        indarrays = [np.arange(0, matrix.shape[0])]

    for group, indarray in zip(ugroups, indarrays):
        for wdt, dec, typ, col, st in zip(wdts, decs, typs, cols, strs):
            sys.stdout.write(st)

            if typ == "g":
                val = group
            elif typ not in STATS:
                sys.stderr.write("Unrecognised type {:s}.".format(typ))
            else:
                values = matrix[indarray, locs[col - 1]].flatten()
                if len(values) == 0:
                    val = 0
                else:
                    val = STATS[typ].function(values)

            if isinstance(val, float):
                sys.stdout.write(formatfloat(val, wdt, dec, seps,
                                             width, precision))
            elif isinstance(val, int):
                sys.stdout.write(formatint(val, wdt, seps, width))
            elif isinstance(val, str):
                sys.stdout.write(formatstr(val, wdt, width))
        sys.stdout.write(strs[-1])


if __name__ == '__main__':
    args, usage = parse_args()
    if (args.input_file_name is None or args.input_file_name == "-") \
       and sys.stdin.isatty():
        sys.stderr.write(usage)
        sys.exit(1)
    main(**vars(args))
