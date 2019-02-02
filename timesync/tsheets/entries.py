"""
Entry points that are used to query the data in the APIs.
"""
import datetime
import logging
from operator import itemgetter

from timesync.tsheets import connection as tsheets
from timesync.utils import configuration as config

import dateutil.parser
from pytz import timezone as py_timezone
import tabulate


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

            LOGGER.info(timesheet)

            # Ignore all records where the record is marked as on the clock
            if timesheet['on_the_clock']:
                LOGGER.warning('Record %s is marked as on the clock.  Skipping..', timesheet['id'])
                continue

            # Check to see if the start and end time have to be generated
            if not timesheet['start'] or not timesheet['end']:
                start_time, end_time = build_start_end_time(timesheet['date'], timesheet['duration'],
                                                            timesheet['tz_str'])
                LOGGER.warning('Record %s does not contain start or end time. Setting to: %s => %s.',
                               timesheet['id'], start_time, end_time)

            else:
                start_time = dateutil.parser.parse(timesheet['start'])
                end_time = dateutil.parser.parse(timesheet['end'])

            timesheet_value = {
                'id': timesheet['id'],
                'start': start_time,
                'end': end_time,
                'duration': timesheet['duration'],
                'date': datetime.datetime.strptime(timesheet['date'], '%Y-%m-%d').date(),
                'notes': timesheet['notes']
            }

            time_entries.append(timesheet_value)

        if not results['more']:
            break

        current_page += 1

    return time_entries


def build_start_end_time(date_string, duration, timezone_str):
    """
    Build a start and end time based on the values from the configuration, and the arguments provided.
    :param str date_string: string containing the date from the record
    :param int duration: number of seconds between start and end time
    :param str timezone_str: string containing the timezone name
    :return tuple containing the start datetime and end datetime
    """
    configuration_start_time = config.get_configuration().get('timeentries', {}).get('default_start_time', '08:00:00')
    configuration_start_time = [int(a) for a in configuration_start_time.split(':')]

    date_value = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    time_value = datetime.time(configuration_start_time[0], configuration_start_time[1], configuration_start_time[2])

    start_time = datetime.datetime.combine(date_value.date(), time_value)
    timezone = py_timezone(timezone_str)
    start_time = timezone.localize(start_time)
    end_time = start_time + datetime.timedelta(seconds=duration)

    return start_time, end_time

