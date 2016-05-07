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

2016/05/05 - TAS - Changed structure to create class BookmarkSet, a set of class Bookmark objects.
                   Added methods to append and delete bookmarks, and to load a set into the
                   UI tree.
"""


import os
import logging
import Tkinter as tk

from collections import MutableMapping, OrderedDict

from rig_remote.constants import CBB_MODES
from rig_remote.disk_io import IO
from rig_remote.exceptions import InvalidPathError, InvalidBookmark, InvalidBookmarkKey
from rig_remote.exceptions import DuplicateBookmark
from rig_remote.utility import frequency_pp_parse, frequency_pp
from rig_remote.constants import LEN_BM
from rig_remote.constants import BM

#logger configuration
logger = logging.getLogger(__name__)

bookmark_keys = ("frequency", "mode", "description", "lock")


def _this_file_exists(filename):
    try:
        with open(filename) as f:
            f.close()
            return(filename)
    except IOError:
        return None

def find_existing_bookmarks_file():
    """ See if we have an existing bookmark file, including defaults from
        previous versions.
        :returns: filename if an existing file is found, None otherwise.
        """

    filename = _this_file_exists(os.path.join(os.getcwd(),"rig-bookmarks.csv"))
    if filename: return filename
    filename = _this_file_exists(os.path.join(os.path.expanduser('~'),
                                            ".rig-remote/rig-bookmarks.csv"))
    if filename: return filename
    filename = _this_file_exists(os.path.join(os.path.expanduser('~'),
                                            ".rig-remote/rig-remote-bookmarks.csv"))
    return filename

class Bookmark(OrderedDict):
    """Bookmark stores an individual bookmark, each instance to contain:
           frequency: a string of digits
           mode: a string from CBB_MODE,
           description: string
           lock: string, either 'O' (Open) or 'L' (Locked)
       and an id_key, for use in mapping to a UI tree element.
    """

    def __init__(self, id_key, *args, **kwargs):
        super(Bookmark, self).__init__(*args, **kwargs)
        self.update(dict(*args, **kwargs))
        self["id_key"] = id_key

class BookmarkSet(object):
    """ BookmarkSet is a list of Bookmarks objects.
        Each instance will have an associated file name stored.
    """

    def __init__(self, filename):

        self.bookmarks = []
        self.filename = filename

    def load_from_file(self):
        """ Load a set of bookmarks from the associated file.
        :raises: InvalidPathError if file not found.
        :raises: InvalidBookmark if an entry is mal-formed.
        """

        bookmark_list = IO()
        try:
            bookmark_list.csv_load(self.filename, ',')
        except InvalidPathError:
            logger.info("No bookmarks file found, skipping.")
            return
        for line in bookmark_list.row_list:
            if len(line) < LEN_BM:
                line.append("O")
            if (line[BM.freq] == '') or (line[BM.mode] not in CBB_MODES):
                raise InvalidBookmark
            else:
                self.bookmarks.append(Bookmark('', zip(bookmark_keys,line)))

    def save_to_file(self):
        """ Save the bookmark set to the associated file."""

        bookmark_list = IO()

        for entry in self.bookmarks:
            bookmark_list.row_list.append(entry.values()[:4])
        bookmark_list.csv_save(self.filename, ',')

    def append(self, id_key, frequency, mode, description = '', lock = ''):
        """ Append a bookmark to the set.
        :raises: InvalidBookmark if entry is mal-formed.
        """

        try:
            int(frequency)
        except (ValueError, TypeError) :
            raise InvalidBookmark
        if (mode not in CBB_MODES) or (lock not in ('O', 'L', '')):
            raise InvalidBookmark
        item = (frequency, mode, description, lock)
        self.bookmarks.append(Bookmark(id_key, zip(bookmark_keys, item)))

    def delete(self, id_key):
        """ Delete a bookmark from the set.
        :raises: InvalidBookmarkKey if key is null string.
        """

        if id_key == '':
            raise InvalidBookmarkKey
        self.bookmarks[:] = [entry for entry in self.bookmarks if entry['id_key'] != id_key]

    def update_id_key(self, id_key, new_id_key):

        entry = next((item for item in self.bookmarks if item['id_key'] == id_key), None)
        if entry == None:
            raise InvalidBookmarkKey
        else:
            entry['id_key'] = new_id_key

    def insert_bookmark_in_tree(self, entry):
        """ Insert a bookmark entry into the UI tree.
        """

        frequency = entry[BM.freq]
        mode = entry[BM.mode]
        idx = tk.END
        for item in self.instance.tree.get_children():
            item_freq = self.instance.tree.item(item).get('values')[BM.freq]
            parsed_item_freq = frequency_pp_parse(item_freq)
            unicode_item_freq = parsed_item_freq.encode("UTF-8")
            item_mode = self.instance.tree.item(item).get('values')[BM.mode]
            if frequency < unicode_item_freq:
                idx = self.instance.tree.index(item)
                break
            elif (frequency == unicode_item_freq and
                          mode == item_mode):
                raise DuplicateBookmark
        entry[BM.freq] = frequency_pp(frequency)
        item = self.instance.tree.insert('', idx, values=entry)
        self.instance.bookmark_bg_tag(item, entry[BM.lockout])
        return item

    def load_bookmark_tree(self, instance):
        """ Load the bookmark set into the UI tree.
        """

        self.instance = instance
        for entry in self.bookmarks :
            entry["id_key"] = self.insert_bookmark_in_tree(entry.values()[:4])



