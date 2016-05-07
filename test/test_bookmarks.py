import pytest
import csv
from rig_remote.bookmarks import BookmarkSet
from rig_remote.exceptions import InvalidBookmark, InvalidBookmarkKey, DuplicateBookmark
from rig_remote.ui import RigRemote
from rig_remote.app_config import AppConfig
import Tkinter as tk

import logging

logger = logging.getLogger(__name__)

def test_bookmark_load():
    mybm = BookmarkSet("./test/test-bookmark-file.csv")
    mybm.load_from_file()

def test_bookmark_load2():
    mybm = BookmarkSet("./test/test-bad-bookmark-file.csv")
    with pytest.raises(InvalidBookmark):
        mybm.load_from_file()

def test_bookmark_load3():
    mybm = BookmarkSet("")
    mybm.load_from_file()

def test_bookmark_save():
    mybm = BookmarkSet("./test/test-bookmark-file.csv")
    mybm.load_from_file()
    mybm.save_to_file()

def test_bookmark_append():
    mybm = BookmarkSet("./test/test-bookmark-file.csv")
    mybm.load_from_file()
    mybm.append('', '155000400', 'CW')
    mybm.append('', '155000400', 'CW', '', 'O')
    with pytest.raises(InvalidBookmark):
        mybm.append('', '', 'CW')
        mybm.append('', '155000400', '')
        mybm.append('', '15500c000', 'CW')
        mybm.append('', '155000400', 'CW', '', 'D')

def test_bokmark_delete():
    mybm = BookmarkSet("./test/test-bookmark-file.csv")
    mybm.load_from_file()
    mybm.append('1001', '100500400', 'CW')
    mybm.delete('1001')
    mybm.delete('1001')
    with pytest.raises(InvalidBookmarkKey):
        mybm.delete('')

def test_load_bookmark_tree():
    root = tk.Tk()
    ac = AppConfig("./test/test-config.file")
    rr = RigRemote(root, ac)
    rr.apply_config(ac)
    mybm = BookmarkSet("./test/test-bookmark-file.csv")
    mybm.load_from_file()
    mybm.load_bookmark_tree(rr)
    rr.root.destroy()

testdata = [['100500600', 'CW','','O']]
@pytest.mark.parametrize("entry", testdata)
def test_insert_bookmark_in_tree(entry):
    root = tk.Tk()
    ac = AppConfig("./test/test-config.file")
    rr = RigRemote(root, ac)
    rr.apply_config(ac)
    mybm = BookmarkSet("./test/test-bookmark-file.csv")
    mybm.load_from_file()
    mybm.load_bookmark_tree(rr)
    mybm.insert_bookmark_in_tree(entry)
    rr.root.destroy()
