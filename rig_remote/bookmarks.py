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

from collections import MutableMapping

from rig_remote.constants import CBB_MODES
from rig_remote.disk_io import IO
from rig_remote.exceptions import InvalidPathError, InvalidBookmark, InvalidBookmarkKey

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

class Bookmark(MutableMapping):
    """Bookmark stores an individual bookmark, each instance to contain:
           frequency: a string of digits
           mode: a string from CBB_MODE,
           description: string
           lock: string, either 'O' (Open) or 'L' (Locked)
       and an id_key, for use in mapping to a UI tree element.
    """

    def __init__(self, id_key, *args, **kwargs):
        self.id_key = id_key
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

class BookmarkSet(object):
    """ BookmarkSet is a list of Bookmarks objects.
        Each instance will have an associated file name stored.
    """

    def __init__(self, filename):

        self.bookmarks = []
        self.filename = filename

    def load_from_file(self):

        bookmark_list = IO()
        try:
            bookmark_list.csv_load(self.filename, ',')
        except InvalidPathError:
            logger.info("No bookmarks file found, skipping.")
            return
        count = 0
        for line in bookmark_list.row_list:
            error = False
            if len(line) < LEN_BM:
                line.append("O")
            if line[BM.freq] == '':
                error = True
            if line[BM.mode] not in CBB_MODES:
                error = True
            if error == True:
                raise InvalidBookmark
            else:
                self.bookmarks.append(Bookmark('', zip(bookmark_keys,line)))

    def save_to_file(self):

        bookmark_list = IO()

        for entry in self.bookmarks:
            btuple = (entry['frequency'], entry['mode'], entry['description'], entry['lock'])
            bookmark_list.row_list.append(btuple)
        bookmark_list.csv_save(self.filename, ',')

    def append(self, id_key, frequency, mode, description = '', lock = ''):

        try:
            int(frequency)
        except (ValueError, TypeError) :
            raise InvalidBookmark
            return
        if mode not in CBB_MODES:
            raise InvalidBookmark
            return
        if lock not in ('O', 'L', ''):
            raise InvalidBookmark
            return
        item = (frequency, mode, description, lock)
        self.bookmarks.append(Bookmark(id_key, zip(bookmark_keys, item)))

    def delete(self, id_key):

        if id_key == '':
            raise InvalidBookmarkKey
            return
        self.bookmarks[:] = [item for item in self.bookmarks if item.id_key != id_key]
