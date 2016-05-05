#!/usr/bin/env python

"""
Remote application that interacts with rigs using rigctl protocol.

Please refer to:
http://gqrx.dk/
http://gqrx.dk/doc/remote-control
http://sourceforge.net/apps/mediawiki/hamlib/index.php?title=Documentation

Author: Rafael Marmelo
Author: Simone Marzona

License: MIT License

Copyright (c) 2014 Rafael Marmelo
Copyright (c) 2015 Simone Marzona
Copyright (c) 2016 Tim Sweeney

TAS - Tim Sweeney - mainetim@gmail.com

2016/05/04 - TAS - First rough draft of part of the Bookmarks class. Can only instantiate itself
                   and load and save itself to a file (if that file exists).

"""


import os
import logging

from rig_remote.constants import CBB_MODES
from rig_remote.disk_io import IO
from rig_remote.exceptions import InvalidPathError

from rig_remote.constants import LEN_BM
from rig_remote.constants import BM

#logger configuration
logger = logging.getLogger(__name__)

bookmark_keys = ("frequency", "mode", "description", "lock")


def this_file_exists(filename):
    try:
        with open(filename) as f:
            f.close()
            return(filename)
    except IOError:
        return None

def find_existing_bookmarks_file():

    filename = this_file_exists(os.path.join(os.getcwd(),"rig-bookmarks.csv"))
    if filename: return filename
    filename = this_file_exists(os.path.join(os.path.expanduser('~'),
                                            ".rig-remote/rig-bookmarks.csv"))
    if filename: return filename
    filename = this_file_exists(os.path.join(os.path.expanduser('~'),
                                            ".rig-remote/rig-remote-bookmarks.csv"))
    return filename


class Bookmarks(object):
    """ Bookmarks is a list of dicts, each dict containing a frequency, mode, description
        and lock value. Each instance will have an associated file name stored.
    """

    def __init__(self, filename):

        self.bookmarks = []
        self.filename = filename

    def load_from_file(self, silent = False):

        bookmark_list = IO()
        try:
            bookmark_list.csv_load(self.filename, ',')
        except InvalidPathError:
            logger.info("No bookmarks file found, skipping.")
            return
        count = 0
        for line in bookmark_list.row_list:
            count += 1
            error = False
            if len(line) < LEN_BM:
                line.append("O")
            if line[BM.freq] == '':
                error = True
            if line[BM.mode] not in CBB_MODES:
                error = True
            if error == True:
                if not silent:
                    tkMessageBox.showerror("Error", "Invalid value in " \
                    "Bookmark #%i. " \
                    "Skipping..." % count)
            else:
                self.bookmarks.append(dict(zip(bookmark_keys,line)))

    def save_to_file(self):
        bookmark_list = IO()

        for entry in self.bookmarks:
            btuple = (entry['frequency'], entry['mode'], entry['description'], entry['lock'])
            bookmark_list.row_list.append(btuple)
        bookmark_list.csv_save(self.filename, ',')