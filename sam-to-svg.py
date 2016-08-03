#!/usr/bin/env python

import sys
import argparse

def cigar_to_aln_len(cigar):
    current_number = ""
    total_length = 0
    for c in cigar:
        if c in "0123456789":
            current_number += c
        elif c in "MD=X":
            total_length += int(current_number)
            current_number = ""
        else:
            current_number = ""
    return total_length

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    prog="sam-to-svg",
    description="Turns SAM file into SVG showing alignments.")
parser.add_argument("sam_file", type=str,
                    help="SAM file.")
parser.add_argument("-l", "--ref_length", type=int,
                    help="Length of reference (taken from SAM file if header is present.")
parser.add_argument("-m", "--min_length", type=int,
                    help="Minimum length of alignment to draw.")

args = parser.parse_args()
# ----- end command line parsing -----

length = args.ref_length
lanes = [[]]

file = open(args.sam_file)
for line in file:
    if line[0] == "@":
        if line[1:3] == "SQ":
            split = line[3:].split()
            for bit in split:
                if bit[0:2] == "LN":
                    length = int(bit[3:])
    else:
        [qname,flag,rname,pos,mapq,cigar,rnext,pnext,tlen,seq,qual,opt] = line.split(None,11)
        aln_len = cigar_to_aln_len(cigar)
        if args.min_length is None or aln_len >= args.min_length:
            inserted = False
            for lane in lanes:
                if len(lane) == 0:
                    lane.append((int(pos),aln_len))
                    inserted = True
                elif lane[-1][0]+lane[-1][1] < int(pos):
                    lane.append((int(pos),aln_len))
                    inserted = True
                    break
            if not inserted:
                lanes.append([(int(pos),aln_len)])

if length is None:
    sys.stderr.write("Error: ref length must be given is SAM header is not present (--ref_length)\n")
    exit(1)

height = len(lanes) * 10 + (len(lanes)-1) * 2
sys.stdout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
sys.stdout.write("<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\"100pt\" height=\"" + str(height) + "pt\" viewBox=\"0 0 100 " + str(height) + "\" version=\"1.1\">\n")
sys.stdout.write("  <g id=\"genes\" style=\"fill:rgb(120,120,250);stroke-width:0;\">\n")
sys.stdout.write("    <rect x=\"0\" y=\"0\" width=\"100\" height=\"" + str(height) + "\" fill=\"none\" />\n")

y = 0
for lane in lanes:
    for aln in lane:
        sys.stdout.write("    <rect x=\"{:f}\" y=\"{:d}\" width=\"{:f}\" height=\"10\" />\n"
                         .format((float(aln[0])/length)*100,
                                 y,
                                 (float(aln[1])/length)*100))
    y += 12

sys.stdout.write("  </g>\n")
sys.stdout.write("</svg>\n")
