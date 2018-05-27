#!/usr/bin/env python

__author__ = "Karthik Channakeshava"
__email__ = "kchannak@gmail.com"

"""
===========================================================
Log analyzer to process log file and get summary statistics
===========================================================

Given an input log file and pattern to look for, determines the lines where
the pattern occurs, computes the average time between the messages where 
pattern occurs and converts the timezone for the time to PST.

Usage: %prog [-f] [-w]

Program to analyze log files

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -f FILE, --file=FILE  Name of log file to process
  -w WORD, --word=WORD  Word to look for in file

"""

import sys
import os
import re
from datetime import datetime, timedelta
from functools import reduce
from optparse import OptionParser
from pytz import timezone


def grep_file(name, pattern):
    """
    Generator to look for a given string in a file

    Arguments:
        name: String name of file to be processed
        look: String to be identified in the file

    Returns:
        line: yields a line of the file with 'pattern'
    """
    # Some checks for invalid input can go here.

    # Process the given file
    patexp = re.compile(pattern)
    with open(name) as f:
        for line in f:
            if patexp.search(line):
                yield line


def get_time(line):
    """
    Function to convert the date string into datetime object

    Returns:
        time object
    """
    patexp = re.compile('- - \[(.*)\]')
    time_log = patexp.findall(line)
    timestamp = datetime.strptime(time_log[0], "%d/%b/%Y:%H:%M:%S %z")
    #print(time_log, timestamp)
    return timestamp


def get_average(lst):
    """
    Function to compute the average of a list of values.

    Arguments:
        list of values: In this case these are timedelta objects

    Returns:
        average: Average value of the timedelta objects
    """
    average = reduce(lambda a,b: a + b, lst) / len(lst)
    return average


def process_line(line):
    """
    Function to output the matching lines with the timestamp converted to
    Pacific Standard Time (PST).

    Arguments:
        line: the line from the file that contains the pattern

    Returns:
        line: updated line with the timezone changed.
    """
    # Format we want 28/Nov/2016:11:50:25 -0800
    fmt = "%d/%m/%Y:%H:%M:%S %z"
    # Format we want Nov 28 11:50:25
    fmt_start = "%b %d %H:%M:%S"

    timeval = get_time(line)
    timeval = timeval.astimezone(timezone('US/Pacific'))
    line = re.sub(r'- - \[.*\]',
                  '- - [{0}]'.format(timeval.strftime(fmt)),
                  line)
    line = re.sub(r'^\w+\s\d+\s\d{2}:\d{2}:\d{2}',
                  '{0}'.format(timeval.strftime(fmt_start)),
                  line)
    return line


def process_args():
    """
    Function to process the command line options and return the filename
    and pattern from the command line.

    Arguments:

    Returns:
        name: string name for the log file to process
        pattern: string to locate in the log file
    """
    parser = OptionParser(usage = "usage: %prog [-f] [-w]",
                          description = "Program to analyze log files",
                          version = "%prog 1.0")
    parser.add_option("-f", "--file", dest="name",
                      help="Name of log file to process", metavar="FILE")
    parser.add_option("-w", "--word", dest="pattern",
                      help="Word to look for in file", metavar="WORD")

    (options, args) = parser.parse_args()
    if options.name is None:
        # parser.print_help()
        parser.error("Log filename is a required option")
    elif options.pattern is None:
        parser.error("Word to search in log file is required option") 

    return options.name, options.pattern


def main(args):
    """
    Main function to handle the log analyzer functionality

    Arguments:

    Returns:

    """
    
    # Get the name and pattern from the user inputs
    name, pattern = process_args()

    count = 0
    timeval = []
    if not os.path.exists(name):
        print ("File does not exist")
        print ("Check the input provided again and enter a valid file")
        return -1

    matching_lines = grep_file(name, pattern)
    for l in matching_lines:
        timeval.append(get_time(l))
        line = process_line(l)
        print(line, end='')
        count += 1

    # Compute average
    if count > 0:
        # if only one line is matching, diff is empty
        diff = [a - b for b, a in zip(timeval[:-1], timeval[1:])]

        # only valid average when more than 1 lines match
        # do not compute average when there is only one match
        if count > 1:
            average = get_average(diff)
            print('Counted word \'' + pattern + '\'', count, 
                  '\n times in', count, 'lines')
            print('Average time between logged lines\n with word:', average)
        else:
            print("Found only one matching line")

        return 0
    else:
        print("Did not find the \'" + pattern + "\' you provided.")
        return -1


if __name__ == "__main__":
    sys.exit(main(sys.argv))


