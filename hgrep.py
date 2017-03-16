#!/usr/bin/env python

# grep the history

import sys
import argparse
import subprocess
from glob import glob
from os.path import expanduser

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

parser.add_argument("--colour", type=str, choices=["never","always","auto"],
                    default="auto", help="Use colour output.")

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

home = expanduser("~")
files = glob(home + "/.history/*" + year + "/*" + month + "/*" + day + "*")
if len(files) > 0:
    try:
        output = subprocess.check_output(["grep", args.string] + files)
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
    if args.colour == "always" or args.colour =="auto" and sys.stdout.isatty():
        sys.stdout.write(colours.GREEN + host + colours.ENDC + " ")
        sys.stdout.write(colours.BLUE + timestamp + colours.ENDC)
    else:
        sys.stdout.write(host + " ")
        sys.stdout.write(timestamp)
    sys.stdout.write(": " + string + "\n")
