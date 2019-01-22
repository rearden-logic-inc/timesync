"""
Module for loading and maintaining configuration values.
"""
from ruamel.yaml import YAML

_configuration = None


def get_configuration(configuration_path='./config.yaml'):
    """
    Return a dict containing configuration values.
    :param str configuration_path: path to parse yaml from.
    :return: dict
    """
    global _configuration

    if _configuration is None:
        parser = YAML(typ='rt')

        with open(configuration_path) as configuration_file:
            _configuration = parser.load(configuration_file)

    return _configuration
