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
    KEYWORD_FUTURE = 'Future'

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
            if not os.path.exists(filename):
                return dict()
            with open(filename) as fd:
                return yaml.load(fd)
        content = load()
        for key in (
                self.KEYWORD_TODO,
                self.KEYWORD_ACCOMPLISHED,
                self.KEYWORD_FUTURE,
                ):
            if key not in content or content[key] is None:
                content[key] = []
        return content

    def create_today_file(self):
        content = self.load_file(self.last_file)
        with open(self.current_file, 'w+') as fd:
            data = content[self.KEYWORD_TODO]
            fd.write('%s:\n' % self.KEYWORD_TODO)
            if data:
                fd.write(yaml.dump(data, default_flow_style=False))
            else:
                fd.write('\n')
            fd.write('\n')

            data = content[self.KEYWORD_ACCOMPLISHED]
            fd.write('%s:\n' % self.KEYWORD_ACCOMPLISHED)
            if data:
                fd.write(yaml.dump(data, default_flow_style=False))
            else:
                fd.write('\n\n')
            fd.write('\n')
        
            data = content[self.KEYWORD_FUTURE]
            fd.write('%s:\n' % self.KEYWORD_FUTURE)
            if data:
                data.sort()
                fd.write(yaml.dump(data, default_flow_style=False))
            else:
                fd.write('\n\n')
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
