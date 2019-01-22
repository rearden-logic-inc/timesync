"""
Processes a script file of tasks.
"""
import argparse
import datetime
import pkg_resources

from timesync.utils import plugins

from ruamel.yaml import YAML

def create_argument_parser(subparser):
    parser = subparser.add_parser('process', help='Process the contents of a script file')

    parser.add_argument('file', type=argparse.FileType('r'), help='file to import the data structure from')

    parser.set_defaults(func=_main)


def _main(args):

    parser = YAML(typ='rt')
    tasks = parser.load(args.file)

    for task in tasks['tasks']:

        if task['type'] == 'copy':
            _copy_processor(task)
        elif task['type'] == 'delete':
            _delete_process(task)


def _copy_processor(configuration):

    dates = [datetime.datetime.now()]

    reader = plugins.load_plugin('timesheet_reader', configuration['from']['id'])

    results = []
    for date in dates:
        results += reader(date, configuration['from'])

    print(f'{results}')

    writer = plugins.load_plugin('timesheet_writer', configuration['to']['id'])

    writer(configuration['to'], results)


def _delete_process(configuration):

    dates = [datetime.datetime.now()]

    deleter = plugins.load_plugin('timesheet_delete', configuration['from']['id'])

    for date in dates:
        deleter(configuration['from'], date)
