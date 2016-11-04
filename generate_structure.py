#!/usr/bin/env python

import sys
import os
import argparse
import glob
from collections import namedtuple
import threading
import time

def contig_short_name(ref,pos):
    [refn,contign] = ref.split("_")
    return "{:s}_{:s}".format(contign,pos)


def isolate_short_name(name):
    return name.split("/")[-1]


def progress(fp, fs, fin):
    progress = ["-", "\\", "|", "/"]
    prog = 0
    while not fin.isSet():
        sys.stderr.write("\r{:3.0f}% {:s}\b".format(fp.tell()/float(fs)*100,
                                                    progress[prog]))
        sys.stderr.flush()
        prog = (prog + 1)%4
        time.sleep(1)
    return


Pos = namedtuple("Pos", ["idx","bases"])

basenum = {"A":"1","T":"2","G":"3","C":"4"}

# ----- command line parsing -----
parser = argparse.ArgumentParser(
    description="Generates STRUCTURE input from positions and synonymous SNP files.")
parser.add_argument("positions_file", type=str, help="Positions file.")
parser.add_argument("isolate_dir", type=str, help="Directory of isolate files.")
parser.add_argument("-m", "--multiallelic", dest="multi", action="store_true",
                    help="Keep multiallelic sites.")
parser.set_defaults(multi=False)

args = parser.parse_args()
# ----- end command line parsing -----

pos_file = open(args.positions_file)
positions = {}
position_names = []
pos_index = 0
for line in pos_file:
    [ref,pos] = line.split()
    sname = contig_short_name(ref,pos)
    positions[sname] = Pos(pos_index, set())
    position_names.append(sname)
    pos_index += 1

matrix = []
default_bases = ["-9" for pos in positions]

isolate_files = glob.glob(args.isolate_dir + "/*")
isolates = 1
sys.stderr.write("Loading isolate files...\n")
for isolate_file_name in isolate_files:
    file_size = os.path.getsize(isolate_file_name)
    sys.stderr.write("Isolate {:d}: {:s}...\n".format(isolates, isolate_short_name(isolate_file_name)))
    isolates += 1
    isolate_file = open(isolate_file_name)
    base1 = list(default_bases)
    base2 = list(default_bases)
    lines = 1
    fin = threading.Event()
    pthread = threading.Thread(name = "progress",
                                target = progress,
                                args = (isolate_file, file_size, fin))
    try:
        pthread.start()
        for line in isolate_file:
            lines += 1
            [ref,pos,refa,alta1,alta2] = line.split()
            sname = contig_short_name(ref,pos)
            if sname in positions:
                base1[positions[sname].idx] = basenum[alta1.upper()]
                positions[sname].bases.add(alta1.upper())
                base2[positions[sname].idx] = basenum[alta2.upper()]
                positions[sname].bases.add(alta2.upper())
        fin.set()
        pthread.join()
    except KeyboardInterrupt:
        fin.set()
        pthread.join()
        isolate_file.close()
        sys.stderr.write("\n")
        sys.exit(1)
    isolate_file.close()
    matrix.append([isolate_short_name(isolate_file_name) + "_1"] + base1)
    matrix.append([isolate_short_name(isolate_file_name) + "_2"] + base2)
    sys.stderr.write("\rDone. ")
    sys.stderr.write("\n")

sys.stderr.write("Classifying sites...\n")
missing_positions = set()
monoallelic_positions = set()
biallelic_positions = set()
other_positions = set()
for position_name in position_names:
    if len(positions[position_name].bases) == 0:
        missing_positions.add(position_name)
    elif len(positions[position_name].bases) == 1:
        monoallelic_positions.add(position_name)
    elif len(positions[position_name].bases) == 2:
        biallelic_positions.add(position_name)
    else:
        other_positions.add(position_name)
    if args.multi or position_name in biallelic_positions or position_name in monoallelic_positions:
        sys.stdout.write("\t" + position_name)
sys.stdout.write("\n")

for row in matrix:
    sys.stdout.write(row[0])
    for position_name in position_names:
        if args.multi or position_name in biallelic_positions or position_name in monoallelic_positions:
            sys.stdout.write("\t" + row[positions[position_name].idx + 1])
    sys.stdout.write("\n")
    
sys.stderr.write("Missing positions:     \t{:d}\n"
                 "Monoallelic positions: \t{:d}\n"
                 "Biallelic positions:   \t{:d}\n"
                 "Multiallelic positions:\t{:d}\n"
                 "Total:                 \t{:d}\n".
                 format(len(missing_positions),
                        len(monoallelic_positions),
                        len(biallelic_positions),
                        len(other_positions),
                        len(missing_positions)+
                        len(monoallelic_positions)+
                        len(biallelic_positions)+
                        len(other_positions)))
