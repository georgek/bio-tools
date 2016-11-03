#!/usr/bin/env python

# this is for checking if the ambiguity code in aligned flanking sequences
# agree with the base in the reference

import sys

comp = {'a':'t', 'c':'g', 'g':'c', 't':'a', 'u':'a',
        'n':'n',
        'r':'y','y':'r','s':'s','w':'w','k':'m','m':'k',
        'b':'v','v':'b','d':'h','h':'d'}
def reverse_complement(string):
    return ''.join(map(lambda c: comp[c], string[::-1].lower()))

basecodes = {}
basecodes["a"] = 0b0001
basecodes["c"] = 0b0010
basecodes["g"] = 0b0100
basecodes["t"] = 0b1000
basecodes["r"] = basecodes["a"]               |basecodes["g"]
basecodes["y"] =                basecodes["c"]               |basecodes["t"]
basecodes["k"] =                               basecodes["g"]|basecodes["t"]
basecodes["m"] = basecodes["a"]|basecodes["c"]
basecodes["s"] =                basecodes["c"]|basecodes["g"]
basecodes["w"] = basecodes["a"]                              |basecodes["t"]
basecodes["b"] =                basecodes["c"]|basecodes["g"]|basecodes["t"]
basecodes["d"] = basecodes["a"]               |basecodes["g"]|basecodes["t"]
basecodes["h"] = basecodes["a"]|basecodes["c"]               |basecodes["t"]
basecodes["v"] = basecodes["a"]|basecodes["c"]|basecodes["g"]
basecodes["n"] = basecodes["a"]|basecodes["c"]|basecodes["g"]|basecodes["t"]

def base_eq(base1, base2):
    base1=base1.lower()
    base2=base2.lower()
    

def read_fasta(fasta):
    seqs = {}
    for line in fasta:
        if line[0] == ">":
            name = line[1:-1]
            seqs[name] = ""
        else:
            seqs[name] += line.strip()
    return seqs

if len(sys.argv) < 4:
    print "usage: prog sam seq ref"
    sys.exit()

samf = open(sys.argv[1])
seqf = open(sys.argv[2])
reff = open(sys.argv[3])

seqs = read_fasta(seqf)
seqf.close()

alns = {}
for line in samf:
    [qname,flag,rname,pos,mapq,cigar,rnext,pnext,tlen,seq,qual,opt] = line.split(None, 11)
    if rname in alns:
        alns[rname].append((qname,pos,flag))
    else:
        alns[rname] = [(qname,pos,flag)]

currentname = ""
currentseq = ""
ncorrect = 0
nwrong = 0
for line in reff:
    if line[0] == ">":
        currentname = line[1:-1]
        continue
    else:
        currentseq = line[:-1]
    if currentname in alns:
        for (qname,pos,flag) in alns[currentname]:
            [name,ambpos] = qname.split(":")
            pos = int(pos)
            ambpos = int(ambpos)
            flag = int(flag)
            ambbase = seqs[qname][ambpos].lower()
            # print "amb: ", ambbase
            if flag & 0x10:
                refbase = reverse_complement(currentseq[pos + ambpos - 1])
            else:
                refbase = currentseq[pos + ambpos - 1].lower()
            # print "seq: ", refbase
            if basecodes[refbase] & basecodes[ambbase]:
                # print "yes"
                ncorrect += 1
            else:
                # print "no"
                nwrong += 1

print "Correct: ", ncorrect
print "Wrong: ", nwrong
