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
    def current_file(self):
        name = datetime.datetime.now().strftime('%Y-%m-%d-logbook.yaml')
        return os.path.join(self.directory, name)

    @property
    def last_file(self):
        logger.debug('looking for files in %s' % self.directory)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        for filename in reversed(sorted(os.listdir(self.directory))):
            if re.match('^\d{4}-\d{2}-\d{2}-logbook.yaml$', filename):
                logger.debug('Found file matching patter: %s' % filename)
                return os.path.join(self.directory, filename)
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


if __name__ == '__main__':
    main()
