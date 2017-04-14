import unittest
import re
import os
import tempfile
import shutil
import datetime
import yaml
from logbook.main import LogBook

CURR_DIR = os.path.dirname(__file__)
TEST_DIR = os.path.join(CURR_DIR, 'examples')
EXAMPLE1_DIR = os.path.join(TEST_DIR, '1')


class LogBookTest(unittest.TestCase):
    def setUp(self):
        self.lb = LogBook(EXAMPLE1_DIR)
        if os.path.exists(self.lb.current_file):
            os.remove(self.lb.current_file)

    def test_current_file_name(self):
        assert re.match(
                '%s/\d{4}-\d{2}-\d{2}-logbook.yaml' % EXAMPLE1_DIR,
                self.lb.current_file
                )

    def test_last_file(self):
        assert self.lb.last_file.endswith('2017-04-01-logbook.yaml')

    def test_load_file_that_does_not_exist(self):
        content = self.lb.load_file(os.path.join(EXAMPLE1_DIR, 'fake'))
        assert content == dict(TODO=[], Accomplished=[], Backlog=[])

    def test_load_file(self):
        filename = os.path.join(EXAMPLE1_DIR, '2017-01-01-logbook.yaml')
        content = self.lb.load_file(filename)
        assert 'TODO' in content
        assert len(content['TODO']) == 1
        assert 'Accomplished' in content
        assert content['Accomplished'] == []
        assert 'Backlog' in content
        assert content['Backlog'] == []

    def test_create_file_for_today(self):
        self.lb.create_today_file()
        assert os.path.exists(self.lb.current_file)


class FromScratchTest(unittest.TestCase):
    def test_create_file_for_today_from_scratch(self):
        directory = tempfile.mkdtemp()
        try:
            self.lb = LogBook(directory)
            self.lb.create_today_file()
            assert os.path.exists(self.lb.current_file)
        finally:
            shutil.rmtree(directory)

class BacklogTest(unittest.TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.lb = LogBook(self.directory)
        
        if os.path.exists(self.lb.current_file):
            os.remove(self.lb.current_file)

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_no_date_wont_change_anything(self):
        filename = os.path.join(self.directory, "2017-01-01-logbook.yaml")
        data = dict(
            Backlog = ['whatever']
        )
        with open(filename, 'w+') as fd:
            yaml.dump(data, fd)
        self.lb.create_today_file()
        content = self.lb.load_file(self.lb.current_file)
        assert not content['TODO'] 

    def test_date_will_move_to_todo(self):
        filename = os.path.join(self.directory, "2017-01-01-logbook.yaml")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        data = dict(
            Backlog = ['[%s] whatever' % today]
        )
        with open(filename, 'w+') as fd:
            yaml.dump(data, fd)
        self.lb.create_today_file()
        content = self.lb.load_file(self.lb.current_file)
        assert not content['Backlog'] 
        assert content['TODO'] == ['whatever']



