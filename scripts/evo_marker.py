#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
evo_marker.py.py: Calculates the mutation rates.

Compares input alignment files in fasta format with a reference fasta file,
generates the output as a tab-separated table with the following columns:
pos: 1-based position
ref: reference allele
alt: alteration allele
following by the columns with mutation rate for each file in the same order as listed:
percentage of the occurrence in the file
"""

import argparse
import os

from Bio import SeqIO

import utils

__author__ = 'Juhlchen'
__copyright__ = 'Copyright © 2015 Yulia Khlystikova'
__version__ = '0.9'


LINES_DELIMITER = '\n'


def process_files(alignment_paths, reference_path, output_path, quiet=False):
    """
    Processes the input fasta files, compares aligned reads with reference
    and writes the mutations with a rate for each file to a tab-separated output file.
    :param alignment_paths: list of fasta files with aligned reads.
    :param reference_path: reference genome fasta file.
    :param output_path: output file.
    :param quiet: not print the progress on standard output
    :type quiet: bool
    :rtype: None
    """
    with open(reference_path) as reader:
        reference_sequence = SeqIO.parse(reader, 'fasta').next().seq
    reference_sequence_len = len(reference_sequence)

    def check_seq(seq_record):
        fasta_seq_len = len(seq_record.seq)
        if reference_sequence_len != fasta_seq_len:
            utils.print_warning(
                '%s: invalid length %s (%s expected)' % (seq_record.description, fasta_seq_len, reference_sequence_len))

    col_names = []
    alignment_number_by_groups = {}
    all_mutations = {}

    for alignment_path in alignment_paths:
        with open(alignment_path) as reader:  # IOException?
            # currently all the sequences of the same group are in the same file
            if not quiet:
                print 'Processing ' + alignment_path
            group_id = os.path.split(alignment_path)[1]
            col_names.append(group_id)
            count = 0
            for fasta in SeqIO.parse(reader, 'fasta'):
                count += 1
                check_seq(fasta)
                alignment = fasta.seq
                for position in range(min(reference_sequence_len, len(alignment))):
                    alignment_val = alignment[position]
                    if reference_sequence[position] != alignment_val:
                        all_mutations.setdefault(position, {}).setdefault(alignment_val, {}).setdefault(group_id, 0)
                        all_mutations[position][alignment_val][group_id] += 1
            alignment_number_by_groups[group_id] = count

    writer = open(output_path, 'w')

    def write_to_file(cols):
        writer.write(utils.COLUMN_DELIMITER.join(cols) + utils.LINES_DELIMITER)

    header = ['pos', 'ref', 'alt']
    header.extend(col_names)
    write_to_file(header)
    positions = all_mutations.keys()
    positions.sort()
    for i in positions:
        reference_val = reference_sequence[i]
        for mutation in all_mutations[i]:
            line = [str(i + 1), reference_val, mutation]
            for group_id in col_names:
                total_count = alignment_number_by_groups[group_id]
                mutation_count = all_mutations[i][mutation].get(group_id, 0)
                line.append(str(round(float(mutation_count) / total_count, 3)))
            write_to_file(line)
    writer.close()
    if not quiet:
        utils.print_result_file(output_path)


def get_argument_parser():
    """
   Composes a argument parser for command line usage.
   :returns: ArgumentParser
   """
    name = 'eve_marker'
    default_output_name = name + '_output.txt'
    parser = argparse.ArgumentParser(
        description='Compares the given alignments with reference file, finds the mutations, '
                    'writes the percentage of each mutation for each file in the output')

    parser.add_argument('alignment_paths', metavar='<alignment_path>', nargs='+', help='path to alignment file')
    parser.add_argument('-d', '--ref', dest='reference_path', metavar='<reference_path>', required=True,
                        help='reference genome fasta file')
    parser.add_argument('-o', '--out', dest='output_path', metavar='<output_path>', default=default_output_name,
                        help='path to output file, default: %s' % default_output_name)
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                        help='don\'t print progress on standard output', default=False)
    return parser


if __name__ == '__main__':
    args = get_argument_parser().parse_args()
    process_files(args.alignment_paths, args.reference_path, args.output_path, args.quiet)
