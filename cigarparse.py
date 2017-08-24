#!/usr/bin/env python3

import sys
import argparse
import re

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Parses the CIGAR string")

args = parser.parse_args()
# ----- end command line parsing -----

opc = "MIDNSHP=X"
fmtstr = "{:d}" + "\t{:d}".join(opc) + "\n"

for line in sys.stdin:
    qname,flag,rname,pos,mapq,cigar,rnext,pnext,tlen,seq,rest = line.split(maxsplit=10)
    rest = rest.split()
    if len(rest) > 1:
        qual = rest[0]
        opts = rest[1:]
    ops = {op: 0 for op in opc}
    for n,op in re.findall("([0-9]+)([" + opc + "])", cigar):
        if op in ops:
            ops[op] += int(n)
    sys.stdout.write("{:s}\t".format(rname))
    sys.stdout.write(fmtstr.format(*[ops[op] for op in opc]))
