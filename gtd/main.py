#!/usr/bin/env python

import os
import sys
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
    LOGFILE_TOP_LEVEL_FIELDS = frozenset([KEYWORD_BACKLOG, KEYWORD_INPROGRESS,
                                          KEYWORD_ACCOMPLISHED])

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
        last_n_files = self.last_n_files(1)
        if last_n_files and len(last_n_files) > 0:
            return last_n_files[0]

    def last_n_files(self, num_files):
        """Search the directory for gtd files, returning the <num_files>
        latest files"""
        assert num_files > 0, "Number of files must be greater than 0"
        logger.debug('Looking for %d files in %s'
                     % (num_files, self.directory))
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

    def load_file(self, filename, is_summary=False):
        """Load a logfile, <filename>, from disk. If <is_summary> then don't
        add the log file fields accomplished, backlog, etc"""
        def load():
            if not filename or not os.path.exists(filename):
                return dict()
            with open(filename) as fd:
                return yaml.load(fd)
        content = load()
        if not is_summary:
            for key in self.LOGFILE_TOP_LEVEL_FIELDS:
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


def log_error_and_exit_user(msg, retcode=1):
    """Logs an error message <msg> to the user on stderr then exits the program
    with return code <retcode> (with the default value of 1)"""
    sys.stderr.write('%s\n' % msg)
    sys.exit(retcode)


def main():
    DEFAULT_EDITOR = os.environ.get('EDITOR')
    DEFAULT_DIRECTORY = os.path.join(
            os.path.expanduser('~'),
            '.pygtd',
            'backlog'
    )

    EDIT_ACTION_DEFAULT = 'today'
    parser = argparse.ArgumentParser(description="Simple backlog")
    # Add actions as mutually exclusive group of independent options. This way
    # they can have their own values (e.g. Summary takes an int which is number
    # of days to summarize, whereas edit takes a day as string) but can't be
    # used at the same time.
    # Keep the default behaviour of opening the current day to edit when no
    # options are specified.
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
            '-e', '--edit',
            nargs='?',
            const=EDIT_ACTION_DEFAULT,
            help='Edit a GTD log file. By default, the current file will be '
                 'opened for editing'
    )
    group.add_argument(
            '-s', '--summary',
            nargs='?',
            const=5,
            type=int,
            help='Build a summary of the accomplished items over the past N '
                 'days. By default, the past 5 days are summarized'
    )
    parser.add_argument(
            '-d', '--directory',
            default=DEFAULT_DIRECTORY,
            help='Directory to be used. "%s" by default' % DEFAULT_DIRECTORY
    )
    parser.add_argument(
            '--editor',
            default=DEFAULT_EDITOR,
            help='Editor to be used. "%s" by default.' % DEFAULT_EDITOR
    )

    args = parser.parse_args()

    gtd = Gtd(args.directory)

    if args.edit:
        if args.edit == EDIT_ACTION_DEFAULT:
            gtd.create_today_file()
            open_editor(args.editor, gtd.current_file)
        else:
            log_error_and_exit_user('Only editing of Today is supported '
                                    'currently')
    elif args.summary is not None:
        if not args.summary > 0:
            log_error_and_exit_user('Number of days for summary must be a '
                                    'positive integer')
        gtd.generate_n_day_summary(args.summary)
        open_editor(args.editor, gtd.summary_file)
    else:
        # The default case if no explicit options are provided is to just edit
        # today's gtd logfile
        gtd.create_today_file()
        open_editor(args.editor, gtd.current_file)


if __name__ == '__main__':
    main()
