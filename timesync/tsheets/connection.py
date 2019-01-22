"""
Connection and access points for the t-sheets API.
"""
import functools
import logging

from timesync.utils import configuration as config

import requests


LOGGER = logging.getLogger(__name__)
API_ROOT = 'https://rest.tsheets.com/api'


@functools.lru_cache(maxsize=1)
def current_user_details():
    """Return data about the current user."""
    return list(_get('v1/current_user')['results']['users'].values())[0]


def current_assignments(current_page=1):
    """
    Retrieve all of the project assignments associated with the current user.  This is used to check configuration and
    to provide a list of all of the tasks that can be used in the configuration file.
    :return: dict
    """
    current_user_id = current_user_details()['id']

    params = {
        'user_ids': current_user_id,
        'active': 'yes',
        'page': current_page
    }

    LOGGER.debug('Parameters %s', params)

    return _get('v1/jobcode_assignments', params)


def get_time_sheets(work_date, job_code, page=1):
    """
    Retrieve all of the time sheets that are associated with the current logged in user.
    :param datetime.date work_date: the date to retrieve the time sheets for.
    :param int job_code: the job code
    :param int page: the page number to retrieve
    :return: list of time sheets for the parameters provided.
    """
    current_user_id = current_user_details()['id']
    query_params = {'jobcode_ids': f'{job_code}',
                    'start_date': work_date.strftime('%Y-%m-%d'),
                    'supplemental_data': 'no',
                    'user_ids': f'{current_user_id}',
                    'page': page
                    }

    return _get('v1/timesheets', query_params)


def _get(api_path, query_parameters=None):
    """Retrieve data from the path provided."""
    headers = _get_headers()
    results = requests.get(f'{API_ROOT}/{api_path}', headers=headers, params=query_parameters)

    return results.json()


@functools.lru_cache(maxsize=1)
def _get_headers():
    """
    Load the configuration file and create the headers required for accessing the harvest apis.
    :return: dictionary of headers
    """
    try:
        connections = config.get_configuration()['connections']
        tsheets_configuration = connections['t-sheets']

        token = tsheets_configuration['token']
    except KeyError:
        raise RuntimeError('T-Sheets Configuration details missing')

    return {'Authorization': f'Bearer {token}'}
