"""
Module for loading and maintaining configuration values.
"""
import logging

from datetime import datetime, timedelta

from ruamel.yaml import YAML

_configuration = None
LOGGER = logging.getLogger(__name__)
DATE_FORMAT_STRING = '%Y-%m-%d'
DEFAULT_CONFIGURATION_FILE = './config.yaml'


def get_configuration(configuration_path=DEFAULT_CONFIGURATION_FILE):
    """
    Return a dict containing configuration values.
    :param str configuration_path: path to parse yaml from.
    :return: dict
    """
    global _configuration

    if _configuration is None:
        LOGGER.debug('Loading configuration: %s', configuration_path)
        parser = YAML(typ='rt')

        try:
            with open(configuration_path) as configuration_file:
                _configuration = parser.load(configuration_file)
        except FileNotFoundError:
            LOGGER.error('Cannot find log file %s', configuration_path)
            raise RuntimeError

    return _configuration


def parse_date(configuration, date_key='date', start_key='start', end_key='end'):
    """
    Parse a date value out of the configuration dictionary provided using the provided keys.  Always returns a list of
    dates.
    :param dict configuration:
    :param str date_key:
    :param str start_key:
    :param str end_key:
    :return: list of dates
    """
    return_value = []

    if configuration[date_key] == 'today':
        return_value.append(datetime.now())
    elif configuration[date_key] == 'yesterday':
        return_value.append(datetime.now() - timedelta(1))
    elif configuration[date_key] == 'range':
        current_date = datetime.strptime(configuration[start_key], DATE_FORMAT_STRING)
        end_date = datetime.strptime(configuration[end_key], DATE_FORMAT_STRING)

        while current_date <= end_date:
            return_value.append(current_date)
            current_date += timedelta(1)
    else:
        return_value.append(datetime.strptime(configuration[date_key], DATE_FORMAT_STRING))

    return return_value
