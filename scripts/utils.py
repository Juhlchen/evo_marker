#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__author__ = 'Juhlchen'
__copyright__ = 'Copyright © 2015 Yulia Khlystikova'
__version__ = '0.9'


COLUMN_DELIMITER = '\t'
LINES_DELIMITER = '\n'


def remove_line_delimiter(line):
    return line.replace(LINES_DELIMITER, '').strip()


def print_error(error_text, exit_program=False):
    error = error_text if isinstance(error_text, list) else [error_text]
    print LINES_DELIMITER.join(error)
    if exit_program:
        exit(1)


def print_warning(error_text):
    error = error_text if isinstance(error_text, list) else [error_text]
    print LINES_DELIMITER.join(error)


def print_result_file(file_path, text=''):
    notice_text = '' if text == '' else ' (%s)' % text
    print 'Result file: "%s"%s' % (file_path, notice_text)


def get_year(description):
    return description.split('/')[3][:4]
