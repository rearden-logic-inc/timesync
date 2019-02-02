"""Collection of disk entry points for manipulating content in files instead of an API."""
import logging

from ruamel.yaml import YAML

LOGGER = logging.getLogger(__name__)


def time_sheet_writer(configuration, records):
    """Write the entries to the file defined in the configuration section."""

    output_structure = {
        'records': records
    }

    parser = YAML(typ='rt')

    try:
        with open(configuration['filename'], 'w') as output_file:
            _configuration = parser.dump(output_structure, output_file)
    except FileNotFoundError:
        LOGGER.error('Cannot write to file %s', configuration['filename'])
        raise RuntimeError
