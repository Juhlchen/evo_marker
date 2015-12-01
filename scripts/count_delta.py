#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
count_delta.py: adds a delta (max - min) column to the input table
"""

import argparse
import os

import utils

__author__ = 'Juhlchen'
__copyright__ = 'Copyright © 2015 Yulia Khlystikova'
__version__ = '0.9'


def compose_output_file_name(input_file_path, min_delta):
    file_name = ['delta_']
    if min_delta is not None and min_delta > 0:
        file_name.extend(['filter_min', str(min_delta)])
    file_name.append(os.path.basename(input_file_path))
    return os.path.join(os.path.dirname(input_file_path), '_'.join(file_name))


def add_delta_f_to_file(input_path, output_path, min_delta=0):
    """    
    Processes the input tab-separated file, calculates the deltaF function for each raw (max - min).
    :param input_path: list of tab-separated file.
    :param output_path: output file.
    :param min_delta: min value of deltaF function required to include the raw to the output
    :rtype: None
    """
    reader = open(input_path, 'r')
    writer = open(output_path, 'w')
    header_line = utils.remove_line_delimiter(reader.readline())
    column_number = len(header_line.split(utils.COLUMN_DELIMITER))
    if column_number < 4:
        utils.print_error(['Invalid header line: ', header_line], True)
    writer.write(header_line + utils.COLUMN_DELIMITER + 'delta_F' + utils.LINES_DELIMITER)

    def process_invalid_line(invalid_line, line_index, text):
        text = ['Line %s: %s' % (line_index, text)]
        if len(invalid_line.strip()) > 0:
            text.append(invalid_line)
        utils.print_warning(text)
        writer.write(invalid_line)

    i = 0
    for l in reader:
        i += 1
        line = utils.remove_line_delimiter(l)

        if len(line.strip()) == 0:
            process_invalid_line(line, i, 'Empty line')
            continue

        tabs = line.split(utils.COLUMN_DELIMITER)
        if len(tabs) < column_number:
            process_invalid_line(line, i, 'Invalid number of values: %s (%s expected)' % (len(tabs), column_number))
            writer.write(l)
            continue

        try:
            column_values = [float(tabs[i]) for i in range(3, len(tabs))]
        except ValueError as e:
            process_invalid_line(line, i, 'Invalid value: %s' % e)
            writer.write(l)
            continue
        delta = round(max(column_values) - min(column_values), 3)
        if delta > min_delta:
            writer.write(line + utils.COLUMN_DELIMITER + str(delta) + utils.LINES_DELIMITER)
    reader.close()
    writer.close()
    utils.print_result_file(output_path, 'for input file "%s"' % input_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate delta function for input table.')

    parser.add_argument('input_paths', metavar='<table_path>', nargs='+',
                        help='path to file to process')
    parser.add_argument('--min_delta_f', nargs='?', type=float, default=0,
                        help='Min value of delta F (default: 0)')
    args = parser.parse_args()

    for path in args.input_paths:
        add_delta_f_to_file(path, compose_output_file_name(path, args.min_delta_f), args.min_delta_f)
