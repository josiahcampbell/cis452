#!/usr/bin/env python
import os
import csv
from math import ceil
from datetime import date, datetime
import getpass as gp
import socket
import sys

TOP = 0

# Record values
SIZE = 0
PATH = 1
IS_DIR = 4
FILE_COUNT = 5

KILOBYTE = 1024
MEGABYTE = 1024 * KILOBYTE
GIGABYTE = 1024 * MEGABYTE


class DuController():

    def __init__(self):
        self.discoveredPaths = set()

    def getAbsolutePath(self, path):
        if not path.startswith('~'):
            return path
        else:
            return os.path.expanduser(path)

    def depthFirstSearch(self, flags, current_path):
        current_stat = os.lstat(current_path)
        self.discoveredPaths.add(current_stat.st_ino)
        size = 0
        file_count = 0
        if os.path.stat.S_ISDIR(current_stat.st_mode):
            sub_paths = []
            for item in os.listdir(current_path):
                item_absolute_path = os.path.join(current_path, item)
                item_stat = os.lstat(item_absolute_path)
                if os.path.islink(item_absolute_path) or \
                    os.path.stat.S_ISSOCK(item_stat.st_mode):
                        continue
                sub_file = self.depthFirstSearch(flags, item_absolute_path)
                size += sub_file[TOP][SIZE]
                file_count += sub_file[TOP][FILE_COUNT]
                sub_paths += sub_file
            size += current_stat.st_size
            access_time = self.get_date_format(current_stat.st_atime)
            modify_time = self.get_date_format(current_stat.st_mtime)
            directory = [(size, current_path, access_time, modify_time, True, file_count)] \
                        + [p for p in sub_paths if p[IS_DIR]]
            if not 's' in flags:
                self.print_directory(flags, directory[TOP])
            return directory
        elif os.path.stat.S_ISREG(current_stat.st_mode):
            """
            Return:
            * 0 size in Bytes
            * 1 Absolute Path
            * 2 Accessed
            * 3 Modified
            * 4 Is Directory
            * 5 File count (always 1)
            """
            access_time = self.get_date_format(current_stat.st_atime)
            modify_time = self.get_date_format(current_stat.st_mtime)
            return [(current_stat.st_size, current_path, access_time, modify_time, False, 1)]

    def print_directory(self, flags, directory):
        output = ''
        if 'h' in flags:
            output += self.get_human_readable(directory[SIZE])
        else:
            output += str(directory[SIZE])
        if 'c' in flags:
            output += '\t' + str(directory[FILE_COUNT])
        output += '\t' + directory[PATH]
        print output

    def get_date_format(self, time):
        try:
            return datetime.fromtimestamp(int(time)).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return ''

    def get_human_readable(self, size):
        if size < MEGABYTE:
            return str(ceil(size / KILOBYTE)) + 'K'
        elif size < GIGABYTE:
            return str(ceil(size / MEGABYTE)) + 'M'
        else:  # must be huuuuge
            return str(ceil(size / GIGABYTE)) + 'G'

    def write_csv(self, du_results):
        filename = 'proj3-' + datetime.now().strftime("%Y-%m-%d-%H:%M:%S") \
                   + '-' + socket.gethostname() + '-' + gp.getuser() + ".csv"
        with open(filename, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
            for record in du_results:
                writer.writerow(record)
        csv_file.close()
