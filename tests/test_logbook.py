import unittest
import re
import os
from logbook.main import LogBook

CURR_DIR = os.path.dirname(__file__)
TEST_DIR = os.path.join(CURR_DIR, 'examples')
EXAMPLE1_DIR= os.path.join(TEST_DIR, '1')


class LogBookTest(unittest.TestCase):
    def setUp(self):
        self.lb = LogBook(EXAMPLE1_DIR)
        if os.path.exists(self.lb.current_file):
            os.remove(self.lb.current_file)

    def test_current_file_name(self):
        assert re.match('%s/\d{4}-\d{2}-\d{2}-logbook.yaml' % EXAMPLE1_DIR, self.lb.current_file)

    def test_last_file(self):
        assert self.lb.last_file.endswith('2017-04-01-logbook.yaml')

    def test_load_file_that_does_not_exist(self):
        content = self.lb.load_file(os.path.join(EXAMPLE1_DIR, 'fake'))
        assert content == dict(TODO=[], Accomplished=[], Future=[])

    def test_load_file(self):
        filename = os.path.join(EXAMPLE1_DIR, '2017-01-01-logbook.yaml')
        content = self.lb.load_file(filename)
        assert 'TODO' in content
        assert len(content['TODO']) == 1
        assert 'Accomplished' in content
        assert content['Accomplished'] == []
        assert 'Future' in content
        assert content['Future'] == []

    def test_create_file_for_today(self):
        self.lb.create_today_file()
        assert os.path.exists(self.lb.current_file)

