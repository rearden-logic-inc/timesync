"""
Connection that handles the request wrapping along with any of the authentication code that is required.
"""
import functools
import logging

from timesync.utils import configuration as config

import requests


LOGGER = logging.getLogger(__name__)
API_ROOT = 'https://api.harvestapp.com'


@functools.lru_cache(maxsize=1)
def current_user_details():
    """Return data about the current user."""
    return _get('v2/users/me')


@functools.lru_cache(maxsize=1)
def get_company_settings():
    """Company settings will determine how to set the values in the time sheets (start/end times, or just duration)"""
    result =  _get('v2/company')
    LOGGER.debug('Company Stats: %s', result)
    return result


@functools.lru_cache(maxsize=1)
def current_assignments(page=1):
    """
    Retrieve all of the project assignments associated with the current user.  This is used to check configuration and
    to provide a list of all of the tasks that can be used in the configuration file.
    :return: dict
    """
    query_params = {'page': page}

    return _get('v2/users/me/project_assignments', query_params)


def get_time_entries(work_date, project_id, current_page=1):
    """
    Retrieve all of the time sheets that are associated with the current logged in user.
    :param datetime.date work_date: the date to retrieve the time sheets for.
    :param int project_id: the job code
    :param int current_page: the page to fetch data of
    :return: list of time sheets for the parameters provided.
    """

    query_params = {'project_id': f'{project_id}',
                    'from': work_date.strftime('%Y-%m-%d'),
                    'to': work_date.strftime('%Y-%m-%d'),
                    'user_id': current_user_details()['id'],
                    'page': current_page
                    }

    return _get('/v2/time_entries', query_params)


def create_time_entry(project_id, task_id, start_time, end_time, notes=None):
    """
    Create a new time entry for the project and task provided between the time hours.  This will check to see if a
    duration should be stored or if start and end time values should be provided.
    :param int project_id:
    :param int task_id:
    :param datetime.datetime start_time:
    :param datetime.datetime end_time:
    :param notes: any additional notes to be stored in the time entry
    :return:
    """
    company_settings = get_company_settings()

    payload = {
        'project_id': project_id,
        'task_id': task_id,
        'spent_date': start_time.strftime('%Y-%m-%d'),
    }

    if notes:
        payload['notes'] = notes

    # Need to store start and end times.
    if company_settings['wants_timestamp_timers']:

        time_format = '%H:%M'
        if company_settings['clock'] == '12h':
            time_format = '%I:%M%p'

        payload['started_time'] = start_time.time().strftime(time_format).lower()
        payload['ended_time'] = end_time.time().strftime(time_format).lower()

    else:
        duration = end_time - start_time

        hours = round(duration.total_seconds() / 3600, 2)
        payload['hours'] = hours

    _post('v2/time_entries', payload)


def delete_time_entry(entry_id):
    return _delete(f'v2/time_entries/{entry_id}')


def _get(api_path, query_parameters=None):
    """Retrieve data from the path provided."""
    headers = _get_headers()
    results = requests.get(f'{API_ROOT}/{api_path}', headers=headers, params=query_parameters)

    return results.json()


def _post(api_path, post_parameters=None):
    headers = _get_headers()

    results = requests.post(f'{API_ROOT}/{api_path}', headers=headers, json=post_parameters)
    return results.json()


def _delete(api_path):
    headers = _get_headers()

    result = requests.delete(f'{API_ROOT}/{api_path}', headers=headers)

    return result.status_code == 200


@functools.lru_cache(maxsize=1)
def _get_headers():
    """
    Load the configuration file and create the headers required for accessing the harvest apis.
    :return: dictionary of headers
    """
    try:
        connections = config.get_configuration()['connections']
        harvest_configuration = connections['harvest']

        token = harvest_configuration['token']
        account_id = harvest_configuration['account_id']
    except KeyError:
        raise RuntimeError('Harvest Configuration details missing')

    return {'Authorization': f'Bearer {token}',
            'Harvest-Account-Id': f'{account_id}',
            'User-Agent': 'timesync (rerobins@reardenlogic.com)'}
