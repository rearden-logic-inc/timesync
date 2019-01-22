"""
Create the sub command for looking up the available task assignments.
"""
from timesync.utils import plugins


def create_argument_parser(subparser):
    parser = subparser.add_parser('task_assignments', help='List all of the task assignments associated with a time '
                                                           'sheet service.')

    parser.add_argument('service', type=str, help='time sheet service to query', default=None)

    parser.set_defaults(func=_main)


def _main(args):

    task_assignment_method = plugins.load_plugin('task_assignments', args.service)
    task_assignment_method()
