#!/usr/bin/env python3

import sys
import os
import argparse

DEFAULT_OUTPUT_DIR = "."
DEFAULT_OUTPUT_PREFIX=None
DEFAULT_CHUNK_SIZE = 30000000
DEFAULT_MIN_QUALITY = 0


def get_args():
    parser = argparse.ArgumentParser(
        description="Make jobs for variant calling on an alignment with split regions.")
    parser.add_argument("ref_file", type=str,
                        help="Reference FASTA file.")
    parser.add_argument("aln_files", type=str, nargs="+", metavar="aln_file",
                        help="Alignment file.")
    parser.add_argument("-o", "--output_dir", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory for job files.")
    parser.add_argument("-p", "--output_prefix", type=str, default=DEFAULT_OUTPUT_PREFIX,
                        help="Output prefix for job files.")
    parser.add_argument("-c", "--chunk_size", type=int, default=DEFAULT_CHUNK_SIZE,
                        help="Maximum size of a chunk in bp.")
    parser.add_argument("-q", "--min_quality", type=int, default=DEFAULT_MIN_QUALITY,
                        help="Minimum quality of alignments to use.")

    parser.add_argument("-f", "--force", dest="force", action="store_true",
                        help="Overwrite existing output files.")
    parser.set_defaults(force=False)

    return parser.parse_args()


def get_sbatch_boilerplate(extra_options=None):
    boilerplate = """#!/bin/bash
#SBATCH -p tgac-medium # partition (queue)
#SBATCH -N 1 # number of nodes
#SBATCH -n 1 # number of tasks
#SBATCH -c 1 # number of tasks
#SBATCH --mem 4000 # memory pool for all cores
#SBATCH -t 2-00:00 # time (D-HH:MM)
#SBATCH -o slurm.%N.%j.out # STDOUT
#SBATCH -e slurm.%N.%j.err # STDERR
source samtools-1.5
source bcftools-1.3.1
"""
    return boilerplate


def write_batch_script(chunk_n, ref_file, aln_files, refs, out_dir, quality=0):
    aln_basenames = [aln_file.split("/")[-1] for aln_file in aln_files]
    if args.output_prefix:
        prefix = args.output_prefix
    else:
        prefix = "-".join(aln_basenames)
    out_name = ("{out_dir:s}/{prefix:s}_chunk_{n:05d}.job"
                .format(out_dir=out_dir, prefix=prefix, n=chunk_n))
    mode = "w" if args.force else "x"
    try:
        with open(out_name, mode) as fout:
            fout.write(get_sbatch_boilerplate())
            fout.write("""
regions=\"{ref_string:s}\"
pipes=\"\"
for bam in {aln_file_string:s}; do
   pipe=$(mktemp -u)
   mkfifo ${{pipe}}
   samtools view -u ${{bam}} ${{regions}} > ${{pipe}} &
   pipes=\"${{pipes}} ${{pipe}}\"
done
samtools mpileup -u -q{quality:d} -t AD,DP -f {ref_file:s} ${{pipes}} \\
   | bcftools call -c -Ob \\
      > {prefix:s}_chunk_{chunk_n:05d}.bcf
rm ${{pipes}}
            """.format(chunk_n=chunk_n,
                       ref_file=ref_file,
                       aln_file_string=" ".join(aln_files),
                       ref_string=" ".join(refs),
                       prefix=prefix,
                       quality=quality))
    except FileExistsError as e:
        print(e, file=sys.stderr)
        exit()


def main(ref_file,
         aln_files,
         output_dir=DEFAULT_OUTPUT_DIR,
         output_prefix=DEFAULT_OUTPUT_PREFIX,
         chunk_size=DEFAULT_CHUNK_SIZE,
         min_quality=DEFAULT_MIN_QUALITY,
         force=False):
    try:
        faidx_f = open(ref_file + ".fai")
    except FileNotFoundError as e:
        sys.stderr.write("Index file for " + ref_file + " not found.\n"
                         "Use samtools faidx " + ref_file + "\n")
        exit()

    current_refs = []
    current_size = 0
    num_chunks = 0
    max_arg_length = round(os.sysconf('SC_ARG_MAX')*0.9)
    current_arg_length = 0
    for line in faidx_f:
        name, length, rest = line.split(maxsplit=2)
        length = int(length)
        if current_size > 0 \
           and ((current_size + length) > chunk_size \
                or (current_arg_length + len(name) + 1) > max_arg_length):
            num_chunks += 1
            write_batch_script(num_chunks,
                               ref_file,
                               aln_files,
                               current_refs,
                               output_dir,
                               min_quality)
            current_refs = []
            current_size = 0
            current_arg_length = 0
        current_refs.append(name)
        current_size += length
        current_arg_length += (len(name) + 1)
    num_chunks += 1
    write_batch_script(num_chunks,
                       ref_file,
                       aln_files,
                       current_refs,
                       output_dir,
                       min_quality)


if __name__ == '__main__':
    args = get_args()
    main(**vars(args))
