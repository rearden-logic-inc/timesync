"""
Command line entry point for the script.
"""
import argparse
import logging

from timesync.subcommands import task_assignments, process


def _build_arguments():
    parser = argparse.ArgumentParser(description='Time Sync Command')

    subparsers = parser.add_subparsers(help='sub-command help')
    task_assignments.create_argument_parser(subparsers)
    process.create_argument_parser(subparsers)

    return parser


def main():
    logging.basicConfig(level=logging.INFO)
    parser = _build_arguments()

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
