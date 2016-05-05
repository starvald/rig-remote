import pytest
import csv
from rig_remote.bookmarks import BookmarkSet
from rig_remote.exceptions import InvalidBookmark
import logging

logger = logging.getLogger(__name__)

def test_bookmark_load():
    mybm = BookmarkSet("./test/test-bookmark-file.csv")
    mybm.load_from_file()

def test_bookmark_load2():
    mybm = BookmarkSet("./test/test-bad-bookmark-file.csv")
    with pytest.raises(InvalidBookmark):
        mybm.load_from_file()

def test_bookmark_save():
    mybm = BookmarkSet("./test/test-bookmark-file.csv")
    mybm.load_from_file()
    mybm.save_to_file()
