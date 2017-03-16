#!/usr/bin/env python

# grep the history

import sys
import argparse
import subprocess
import glob
import os.path

class colours:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ENDC = '\033[0m'

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Greps the history with optional date restrictions")

parser.add_argument("string", type=str,
                    help="The search string.")
parser.add_argument("year", type=str, nargs="?", default="",
                    help="Restrict search to YEAR.")
parser.add_argument("month", type=str, nargs="?", default="",
                    help="Restrict search to MONTH.")
parser.add_argument("day", type=str, nargs="?", default="",
                    help="Restrict search to DAY.")

parser.add_argument("--color", type=str, choices=["never","always","auto"],
                    default="auto", help="Use colour output.")
parser.add_argument("--histdir", type=str, default="~/.history",
                    help="History directory location (default ~/.history)")

args = parser.parse_args()
# ----- end command line parsing -----

year = args.year
if len(args.month) == 1:
    month = "0" + args.month
else:
    month = args.month
if len(args.day) == 1:
    day = "0" + args.day
else:
    day = args.day

historydir = os.path.expanduser(args.histdir)
if not os.path.isdir(historydir):
    sys.stderr.write(historydir + " does not exist.\n")
    exit(2)

files = sorted(glob.glob(historydir + "/*" +
                         year + "/*" + month + "/*" + day + "*"))

if args.color == "always" or args.color =="auto" and sys.stdout.isatty():
    colourarg = "--color=always"
else:
    colourarg = "--color=never"

if len(files) > 0:
    try:
        output = subprocess.check_output(["grep", colourarg, args.string] + files)
    except subprocess.CalledProcessError as e:
        # grep finds nothing
        exit(e.returncode)
else:
    exit(1)

matches = output.strip().split("\n")
for match in matches:
    [location,string] = match.split(":", 1)
    [year,month,daytimehost] = location.split("/")[-3:]
    [daytime,host,pid] = daytimehost.split("_",2)
    [day,hour,minute,second] = daytime.split(".",3)
    timestamp = "({:s}-{:s}-{:s} {:s}:{:s})".format(
        year, month, day, hour, minute)
    if args.color == "always" or args.color =="auto" and sys.stdout.isatty():
        sys.stdout.write(colours.GREEN + host + colours.ENDC + " ")
        sys.stdout.write(colours.BLUE + timestamp + colours.ENDC)
    else:
        sys.stdout.write(host + " ")
        sys.stdout.write(timestamp)
    sys.stdout.write(": " + string + "\n")
