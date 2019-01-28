"""
Command line entry point for the script.
"""
import argparse
import logging
import sys

from timesync.subcommands import task_assignments, process
from timesync.utils import configuration


def _build_arguments():
    parser = argparse.ArgumentParser(description='Time Sync Command')

    parser.add_argument('-c', '--config',
                        help=f'Specify a configuration file, default is {configuration.DEFAULT_CONFIGURATION_FILE}')

    subparsers = parser.add_subparsers(help='sub-command help')
    task_assignments.create_argument_parser(subparsers)
    process.create_argument_parser(subparsers)

    return parser


def main():
    logging.basicConfig(level=logging.INFO)
    parser = _build_arguments()

    args = parser.parse_args()

    try:
        # Load up the configuration file if the argparser has a configuration file to load.
        if args.config is not None:
            configuration.get_configuration(args.config)

        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    except RuntimeError:
        sys.exit(-1)


if __name__ == '__main__':
    main()
