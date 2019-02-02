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
        raise RuntimeError(f'Cannot write to file {configuration["filename"]}')


def time_entry_reader(date, configuration):
    """Read the entries and return a list of entries that are apart of the date provided."""
    parser = YAML(typ='rt')
    date = date.date()

    try:
        with open(configuration['filename'], 'r') as data_file:
            time_entries = parser.load(data_file).get('records', [])
    except FileNotFoundError:
        LOGGER.error('Cannot read file %s', configuration['filename'])
        raise RuntimeError(f'Cannot read file {configuration["filename"]}')

    return [te for te in time_entries if te['date'] == date]
