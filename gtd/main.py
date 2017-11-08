#!/usr/bin/env python

import os
import re
import argparse
import datetime
import logging
import subprocess
import yaml


logger = logging.getLogger(__name__)


class Gtd(object):
    KEYWORD_TODO = 'TODO'
    KEYWORD_INPROGRESS = 'In progress'
    KEYWORD_ACCOMPLISHED = 'Accomplished'
    KEYWORD_BACKLOG = 'Backlog'

    def __init__(self, directory):
        self.directory = directory

    @property
    def summary_file(self):
        return os.path.join(self.directory, 'summary.yaml')

    @property
    def current_file(self):
        name = datetime.datetime.now().strftime('%Y-%m-%d-logbook.yaml')
        return os.path.join(self.directory, name)

    @property
    def last_file(self):
        """Return the last file in the logbook directory"""
        return self.last_n_files(1)[0]

    def last_n_files(self, num_files):
        """Search the directory for gtd files, returning the <num_files>
        latest files"""
        assert num_files>0, "Number of files must be greater than 0"
        logger.debug('Looking for %d files in %s' % (num_files, self.directory))
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        files_found = []
        _num_files = num_files
        for filename in reversed(sorted(os.listdir(self.directory))):
            if re.match('^\d{4}-\d{2}-\d{2}-logbook.yaml$', filename):
                logger.debug('Found file matching pattern: %s' % filename)
                files_found.insert(0, os.path.join(self.directory, filename))
                _num_files -= 1
                if not _num_files:
                    # We've found all our files
                    break

        if len(files_found) > 0:
            return files_found
        logger.debug('no files found')

    def load_file(self, filename):
        def load():
            if not filename or not os.path.exists(filename):
                return dict()
            with open(filename) as fd:
                return yaml.load(fd)
        content = load()
        for key in (
                self.KEYWORD_INPROGRESS,
                self.KEYWORD_ACCOMPLISHED,
                self.KEYWORD_BACKLOG,
                ):
            if key not in content or content[key] is None:
                content[key] = []
        if self.KEYWORD_TODO in content:
            content[self.KEYWORD_INPROGRESS].extend(
                content[self.KEYWORD_TODO]
            )
        return content

    def create_today_file(self):
        if self.last_file == self.current_file:
            # already created
            return
        content = self.load_file(self.last_file)
        content[self.KEYWORD_ACCOMPLISHED] = None
        backlog = []

        for entry in content[self.KEYWORD_BACKLOG]:
            if isinstance(entry, dict):
                line = list(entry.keys())[0]
            else:
                line = entry
            m = re.match('\[(?P<date>\d{4}-\d{2}-\d{2})\](?P<msg>.*)', line)
            if not m:
                backlog.append(entry)
                continue
            date = datetime.datetime.strptime(m.group('date'), '%Y-%m-%d')
            if date > datetime.datetime.now():
                backlog.append(entry)
                continue
            content[self.KEYWORD_INPROGRESS].insert(0, entry)
        content[self.KEYWORD_BACKLOG] = backlog

        with open(self.current_file, 'w+') as fd:
            operations = (
                (self.KEYWORD_INPROGRESS, False),
                (self.KEYWORD_ACCOMPLISHED, False),
                (self.KEYWORD_BACKLOG, True),
            )
            for key, sort in operations:
                data = content[key]
                fd.write('%s:\n' % key)
                if data:
                    if sort:
                        cmp_fn = (
                            lambda x:
                            list(x.keys())[0]
                            if isinstance(x, dict)
                            else x
                        )
                        data.sort(key=cmp_fn)
                    fd.write(yaml.dump(data, default_flow_style=False))
                else:
                    fd.write('\n')
                fd.write('\n')

    def get_date_from_file(self, log_file):
        """Return the date for a given gtd log file, <log_file> (path or
        filename). Returns None if no date can be identified
        """
        # Get just the filename
        log_day_filename = os.path.basename(os.path.normpath(log_file))

        match_obj = re.match('(?P<date>\d{4}-\d{2}-\d{2})(?P<suffix>.*)',
                             log_day_filename)
        if match_obj:
            return datetime.datetime.strptime(match_obj.group('date'),
                                              '%Y-%m-%d')


    def generate_n_day_summary(self, num_days):
        """Generate a summary of the work done over <num_days>"""
        with open(self.summary_file, 'w') as summary_file_fd:

            for log_day_path in self.last_n_files(num_days):
                log_day_date = self.get_date_from_file(log_day_path)\
                                .strftime('%Y-%m-%d')
                # log_day_date = log_day_date.strftime('%Y-%m-%d')

                # deserialize the file contents into a yaml object
                log_day_yaml = self.load_file(log_day_path)

                # Write header for the day
                summary_file_fd.write('%s:\n' % log_day_date)

                # Write what was accomplished that day
                accomplished_items = log_day_yaml[self.KEYWORD_ACCOMPLISHED]
                if not accomplished_items:
                    accomplished_items.append("N/A - No Data")
                summary_file_fd.write(yaml.dump(accomplished_items,
                                                default_flow_style=False))

                # Add a bit of space between the items to prettify it
                summary_file_fd.write('\n')


def open_editor(editor, filename):
    if editor is None:
        print(
            'No editor was chosen.'
            ' Please, define the environment variable "EDITOR"'
            ' or just use the -d option to especify it.'
        )
        return
    subprocess.call([editor, filename])


def main():
    DEFAULT_EDITOR = os.environ.get('EDITOR')
    DEFAULT_DIRECTORY = os.path.join(
            os.path.expanduser('~'),
            '.pygtd',
            'backlog'
    )

    ACTION_EDIT_TODAY = 'today'
    ACTION_SUMMARY = 'summary'
    parser = argparse.ArgumentParser(description="Simple backlog")
    parser.add_argument(
            'action',
            default=ACTION_EDIT_TODAY,
            nargs='?',
            help='Action to be performed.'
            ' By default, current file will be open'
    )
    parser.add_argument(
            '-d', '--directory',
            default=DEFAULT_DIRECTORY,
            help='Directory to be used. "%s" by default' % DEFAULT_DIRECTORY
    )
    parser.add_argument(
            '-e', '--editor',
            default=DEFAULT_EDITOR,
            help='Editor to be used. "%s" by default.' % DEFAULT_EDITOR
    )

    args = parser.parse_args()

    gtd = Gtd(args.directory)

    if args.action == ACTION_EDIT_TODAY:
        gtd.create_today_file()
        open_editor(args.editor, gtd.current_file)
    elif args.action == ACTION_SUMMARY:
        gtd.generate_n_day_summary(5)
        open_editor(args.editor, gtd.summary_file)



if __name__ == '__main__':
    main()
