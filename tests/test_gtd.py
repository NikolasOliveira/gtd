import unittest
import re
import os
import tempfile
import shutil
import datetime
import yaml
from gtd.main import Gtd

CURR_DIR = os.path.dirname(__file__)
TEST_DIR = os.path.join(CURR_DIR, 'examples')
EXAMPLE1_DIR = os.path.join(TEST_DIR, '1')


class GtdTest(unittest.TestCase):
    def setUp(self):
        self.gtd = Gtd(EXAMPLE1_DIR)
        if os.path.exists(self.gtd.current_file):
            os.remove(self.gtd.current_file)

    def test_current_file_name(self):
        assert re.match(
                '%s/\d{4}-\d{2}-\d{2}-logbook.yaml' % EXAMPLE1_DIR,
                self.gtd.current_file
                )

    def test_last_file(self):
        assert self.gtd.last_file.endswith('2017-04-01-logbook.yaml')

    def test_load_file_that_does_not_exist(self):
        content = self.gtd.load_file(os.path.join(EXAMPLE1_DIR, 'fake'))
        assert content == {
            "In progress": [],
            "Accomplished": [],
            "Backlog": []
        }
        filename = os.path.join(EXAMPLE1_DIR, '2017-01-01-logbook.yaml')
        content = self.gtd.load_file(filename)
        assert 'In progress' in content
        assert len(content['In progress']) == 1
        assert 'Accomplished' in content
        assert content['Accomplished'] == []
        assert 'Backlog' in content
        assert content['Backlog'] == []

    def test_create_file_for_today(self):
        self.gtd.create_today_file()
        assert os.path.exists(self.gtd.current_file)


class FromScratchTest(unittest.TestCase):
    def test_create_file_for_today_from_scratch(self):
        directory = tempfile.mkdtemp()
        try:
            self.gtd = Gtd(directory)
            self.gtd.create_today_file()
            assert os.path.exists(self.gtd.current_file)
        finally:
            shutil.rmtree(directory)


class BacklogTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.gtd = Gtd(self.directory)

        if os.path.exists(self.gtd.current_file):
            os.remove(self.gtd.current_file)

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_no_date_wont_change_anything(self):
        filename = os.path.join(self.directory, "2017-01-01-logbook.yaml")
        data = dict(
            Backlog=['whatever']
        )
        with open(filename, 'w+') as fd:
            yaml.dump(data, fd)
        self.gtd.create_today_file()
        content = self.gtd.load_file(self.gtd.current_file)
        assert not content['In progress']

    def test_date_will_move_to_todo(self):
        filename = os.path.join(self.directory, "2017-01-01-logbook.yaml")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        task = '[%s] whatever' % today
        data = dict(
            Backlog=[task]
        )
        with open(filename, 'w+') as fd:
            yaml.dump(data, fd)
        self.gtd.create_today_file()
        content = self.gtd.load_file(self.gtd.current_file)
        assert not content['Backlog']
        assert content['In progress'] == [task]

    def test_several_dates(self):
        filename = os.path.join(self.directory, "2017-01-01-logbook.yaml")
        today = datetime.datetime.now()
        tomorrow = (today + datetime.timedelta(days=1))
        yesterday = (today - datetime.timedelta(days=1))
        past_task = '[%s] past' % yesterday.strftime("%Y-%m-%d")
        current_task = '[%s] current' % today.strftime("%Y-%m-%d")
        future_task = '[%s] future' % tomorrow.strftime("%Y-%m-%d")
        any_task = 'anything'
        data = dict(
            Backlog=[
                past_task,
                current_task,
                future_task,
                any_task,
            ]
        )
        with open(filename, 'w+') as fd:
            yaml.dump(data, fd)
        self.gtd.create_today_file()
        content = self.gtd.load_file(self.gtd.current_file)
        assert content['Backlog'] == [future_task, any_task]
        assert content['In progress'] == [current_task, past_task]
