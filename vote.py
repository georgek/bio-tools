#!/usr/bin/env python

# votes values into groups

import sys
import argparse

# ----- command line parsing -----

parser = argparse.ArgumentParser(
    prog="vote",
    description="Votes values into groups.")
parser.add_argument("-c", "--data_column", type=int, default=1,
                    help="Column to group with.")
parser.add_argument("-v", "--vote_column", type=int, default=2,
                    help="Column to vote with.")
parser.add_argument("-t", "--threshold", type=float, default=0.5,
                    help="Threshold for making a call.")
parser.add_argument("-d", "--delimiter", type=str, default=None,
                    help="Column delimiter.")

args = parser.parse_args()
# ----- end command line parsing -----

votes = {}

for line in sys.stdin:
    split = line.split(args.delimiter)
    data = split[args.data_column - 1]
    vote = split[args.vote_column - 1]
    if data in votes:
        if vote in votes[data]:
            votes[data][vote] += 1
        else:
            votes[data][vote] = 1
    else:
        votes[data] = {vote : 1}

for data in votes:
    maxn = 0
    for vote in votes[data]:
        if votes[data][vote] > maxn:
            maxv = vote
            maxn = votes[data][vote]
    sys.stdout.write("{:s}\t{:s}\n".format(data, maxv))
