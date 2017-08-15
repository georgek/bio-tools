#!/usr/bin/env python3

import sys
import os
import argparse

DEFAULT_MIN_QUALITY = 30
DEFAULT_PHRED = 33

def get_args():
    parser = argparse.ArgumentParser(
        description="Filter SAM for average read quality.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-q", "--min_quality", type=int, default=DEFAULT_MIN_QUALITY,
                        help="Minimum average read quality.")
    parser.add_argument("-p", "--phred", type=int, default=DEFAULT_PHRED,
                        help="Phred quality score type.")
    return parser.parse_args()


def main(min_quality=DEFAULT_MIN_QUALITY,
         phred=DEFAULT_PHRED):
    for line in sys.stdin:
        qname,flag,rname,pos,mapq,cigar,rnext,pnext,tlen,seq,qual,rest = line.split(maxsplit=11)
        base_quals = [ord(qchar) - phred for qchar in qual]
        avg_quality = sum(base_quals)/len(base_quals)
        if avg_quality > min_quality:
            sys.stdout.write(line)


if __name__ == '__main__':
    args = get_args()
    main(**vars(args))
