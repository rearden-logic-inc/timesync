"""
Entry points that are used to query the data in the APIs.
"""
import logging
from operator import itemgetter

from timesync.tsheets import connection as tsheets

import tabulate
import dateutil.parser

LOGGER = logging.getLogger(__name__)


def task_assignments():
    """
    Retrieve all of the task assignments that are associated with the currently logged in user.
    """
    current_page = 1

    jobcodes = {}

    # Need to loop over this until there is no more data to use
    while True:
        assignment_data = tsheets.current_assignments(current_page)

        for jobcode_assignment in assignment_data['results']['jobcode_assignments'].values():

            jobcode_id = jobcode_assignment['jobcode_id']
            jobcodes[jobcode_id] = {'id': jobcode_id}

        for jobcode_definition in assignment_data['supplemental_data']['jobcodes'].values():
            definition = jobcodes.setdefault(jobcode_definition['id'], {})

            definition['name'] = jobcode_definition['name']
            definition['parent_id'] = jobcode_definition['parent_id']

        if assignment_data['more'] is False:
            break

        current_page += 1
        LOGGER.debug('Fetching page: %s', current_page)

    data_rows = []
    for jobcode_value in jobcodes.values():
        if jobcode_value['parent_id'] != 0:
            results = [jobcode_value['parent_id'], jobcodes[jobcode_value['parent_id']]['name']]
        else:
            results = [0, '']

        results.append(jobcode_value['id'])
        results.append(jobcode_value['name'])

        data_rows.append(results)

    data_rows = sorted(data_rows, key=itemgetter(0, 2))

    headers = ['Parent Id', 'Parent Name', 'Job Code Id', 'Job Code Name']
    print(tabulate.tabulate(data_rows, headers, tablefmt='simple'))


def time_entry_reader(date_value, configuration):
    """Read the time sheet entries from the API and return them to the caller."""
    current_page = 1

    try:
        jobcode = configuration['jobcode']
    except KeyError:
        raise RuntimeError('Could not find jobcode to copy from')

    time_entries = []

    LOGGER.debug(f'processing values for date: {date_value}')

    while True:
        results = tsheets.get_time_sheets(date_value, jobcode, page=current_page)

        LOGGER.debug(f'{results}')

        timesheets = results['results']['timesheets']

        if not timesheets:
            LOGGER.info('No timesheets available for date: %s', date_value)
            return time_entries

        for timesheet in timesheets.values():

            LOGGER.debug(f"timesheet: {timesheet}")

            LOGGER.debug(f"start {timesheet['start']}")
            LOGGER.debug(f"end {timesheet['end']}")

            timesheet_value = {
                'start': dateutil.parser.parse(timesheet['start']),
                'end': dateutil.parser.parse(timesheet['end']),
                'duration': timesheet['duration'],
                'date': timesheet['date'],
                'notes': timesheet['notes']
            }

            time_entries.append(timesheet_value)

        if not results['more']:
            break

        current_page += 1

    return time_entries
