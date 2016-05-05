import pytest
import csv
from rig_remote.bookmarks import Bookmarks
import logging

logger = logging.getLogger(__name__)

def test_bookmark_load():
    mybm = Bookmarks("./test/test-bookmark-file.csv")
    mybm.load_from_file()

def test_bookmark_save():
    mybm = Bookmarks("./test/test-bookmark-file.csv")
    mybm.load_from_file()
    mybm.save_to_file()
