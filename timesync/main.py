"""
Command line entry point for the script.
"""
import argparse
import logging
import logging.config
import pkg_resources
import sys


from timesync.subcommands import task_assignments, process
from timesync.utils import configuration

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError as YAMLParserError


def _build_arguments():
    parser = argparse.ArgumentParser(description='Time Sync Command')

    parser.add_argument('-c', '--config',
                        help=f'Specify a configuration file, default is {configuration.DEFAULT_CONFIGURATION_FILE}')
    parser.add_argument('-l', '--logger-config',
                        help=f'Specify a logger configuration file.  If not defined, default configuration is used.')

    subparsers = parser.add_subparsers(help='sub-command help')
    task_assignments.create_argument_parser(subparsers)
    process.create_argument_parser(subparsers)

    return parser


def main():
    parser = _build_arguments()
    args = parser.parse_args()

    # Configure logging for the application
    if args.logger_config:
        try:
            with open(args.logger_config) as logging_configuration:
                yaml_parser = YAML(typ='rt')
                logging_definition = yaml_parser.load(logging_configuration)
            logging.config.dictConfig(logging_definition)
        except FileNotFoundError:
            logger = logging.getLogger(__name__)
            logger.error('Could not find file: %s', args.logger_config)
            sys.exit(-1)
        except YAMLParserError as ype:
            logger = logging.getLogger(__name__)
            logger.error('Error parsing YAML file. %s', ype.problem_mark)
            sys.exit(-1)
        except KeyError:
            logger = logging.getLogger(__name__)
            logger.error('Error processing logger configuration.')
            logger.error('See: https://docs.python.org/3/library/logging.config.html#logging-config-dictschema')
            sys.exit(-1)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    # Display the version information for the application.
    version_information = pkg_resources.get_distribution('timesync').version
    logger.info(f'Time Sync -- Version: %s', version_information)

    try:
        # Load up the configuration file if the argparser has a configuration file to load.
        if args.config is not None:
            configuration.get_configuration(args.config)

        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    except RuntimeError as rte:
        logger.error(rte)
        sys.exit(-1)


if __name__ == '__main__':
    main()
