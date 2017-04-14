#!/usr/bin/env python

import os
import re
import argparse
import datetime
import logging
import yaml


logger = logging.getLogger(__name__)


class LogBook(object):
    KEYWORD_TODO = 'TODO'
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
                self.KEYWORD_TODO,
                self.KEYWORD_ACCOMPLISHED,
                self.KEYWORD_BACKLOG,
                ):
            if key not in content or content[key] is None:
                content[key] = []
        return content

    def create_today_file(self):
        content = self.load_file(self.last_file)
        content[self.KEYWORD_ACCOMPLISHED] = None
        backlog = []

        for line in content[self.KEYWORD_BACKLOG]:
            m = re.match('\[(?P<date>\d{4}-\d{2}-\d{2})\](?P<msg>.*)', line)
            if not m:
                backlog.append(line)
                continue
            date = datetime.datetime.strptime(m.group('date'), '%Y-%m-%d')
            if date > datetime.datetime.now():
                backlog.append(line)
                continue
            content[self.KEYWORD_TODO].append(m.group('msg').strip())
        content[self.KEYWORD_BACKLOG] = backlog

        with open(self.current_file, 'w+') as fd:
            operations = (
                (self.KEYWORD_TODO, False),
                (self.KEYWORD_ACCOMPLISHED, False),
                (self.KEYWORD_BACKLOG, False),
            )
            for key, sort in operations:
                data = content[key]
                fd.write('%s:\n' % key)
                if data:
                    if sort:
                        data.sort()
                    fd.write(yaml.dump(data, default_flow_style=False))
                else:
                    fd.write('\n')
                fd.write('\n')


def process(args):
    for filename in os.listdir(args.directory):
        print(filename)


def main():
    parser = argparse.ArgumentParser(description="Simple TODO list")
    parser.add_argument(
            '-k', '--key',
            nargs='*',
            default=['TODO', 'Accomplished', '*Future'],
            help='Keywords that can be used. '
            'Everything else will be discarted.'
    )
    parser.add_argument(
            '-d', '--directory',
            default='.',
            help='Directory to be used'
    )

    args = parser.parse_args()
    process(args)


if __name__ == '__main__':
    main()
