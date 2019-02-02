"""
Processes a script file of tasks.
"""
import argparse
import logging

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError as YAMLParserError

from timesync.utils import plugins
from timesync.utils.configuration import parse_date

LOGGER = logging.getLogger(__name__)


def create_argument_parser(subparser):
    parser = subparser.add_parser('process', help='Process the contents of a script file')

    parser.add_argument('file', type=argparse.FileType('r'), help='file to import the data structure from')

    parser.set_defaults(func=_main)


def _main(args):

    parser = YAML(typ='rt')
    try:
        tasks = parser.load(args.file)
    except YAMLParserError as ype:
        raise RuntimeError(f'Cannot parse process file {args.file.name}, see {ype.problem_mark}')

    for task in tasks['tasks']:

        if task['type'] == 'copy':
            _copy_processor(task)
        elif task['type'] == 'delete':
            _delete_process(task)


def _copy_processor(configuration):

    dates = parse_date(configuration)

    reader = plugins.load_plugin('timesheet_reader', configuration['from']['id'])
    writer = plugins.load_plugin('timesheet_writer', configuration['to']['id'])

    results = []
    for date in dates:
        results += reader(date, configuration['from'])

    LOGGER.debug(f'Results : {results}')

    writer(configuration['to'], results)


def _delete_process(configuration):

    dates = parse_date(configuration)

    deleter = plugins.load_plugin('timesheet_delete', configuration['from']['id'])

    for date in dates:
        deleter(configuration['from'], date)
