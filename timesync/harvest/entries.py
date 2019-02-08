"""
Entry points that are used to query the data in the APIs.
"""
import logging

from timesync.harvest import connection as harvest

import tabulate

LOGGER = logging.getLogger(__name__)


def time_entries(date, project_id):
    """
    Generator that iterates through all of the time entries of a specified day and project.
    :return:
    """
    current_page = 1

    while True:
        _time_entries = harvest.get_time_entries(date, project_id, current_page)

        for time_entry in _time_entries['time_entries']:
            yield time_entry

        current_page = _time_entries['next_page']
        if current_page is None:
            break


def project_assignments():
    """
    Generator that will provide all of the assignments that a user has
    :return:
    """
    current_page = 1
    while True:

        assignment_data = harvest.current_assignments(current_page)

        for project_assignment in assignment_data['project_assignments']:
            yield project_assignment

        current_page = assignment_data['next_page']
        if current_page is None:
            break


def task_assignments():
    """
    Retrieve all of the task assignments that are associated with the currently logged in user.
    """
    data_rows = []

    for project_assignment in project_assignments():

        project_id = project_assignment['project']['id']
        project_name = project_assignment['project']['name']

        for task_assignment in project_assignment['task_assignments']:

            if task_assignment['is_active']:

                task_id = task_assignment['task']['id']
                task_name = task_assignment['task']['name']

                data_rows.append((project_id, project_name, task_id, task_name, task_assignment['id']))

    headers = ['Project Id', 'Project Name', 'Task Id', 'Task Name', 'Task Assignment']
    print(tabulate.tabulate(data_rows, headers, tablefmt='simple'))


def time_sheet_writer(configuration, records):
    """"
    Write the records to the harvest application defined by configuration.
    """

    try:
        task_id = configuration['task']
        project_id = configuration['project']
    except KeyError:
        raise RuntimeError('Harvest writer is not configured properly')

    for record in records:
        notes = record['notes']
        harvest.create_time_entry(project_id, task_id, record['start'], record['end'], notes)


def time_sheet_delete(configuration, date):
    """
    Delete all of the time entries for the date and configuration provided.
    :param configuration:
    :param date:
    :return:
    """

    try:
        task_id = configuration['task']
        project_id = configuration['project']
    except KeyError:
        raise RuntimeError('Harvest writer is not configured properly')

    # First need to find all of the work assignment identifiers from the project based on the task id provided.
    found_task_assignments = []
    for project_assignment in project_assignments():
        if project_assignment['project']['id'] == project_id:

            for task_assignment in project_assignment['task_assignments']:
                if task_assignment['task']['id'] == task_id:
                    found_task_assignments.append(task_assignment['id'])

    LOGGER.debug(f'Found task assignments: %s', found_task_assignments)

    entries_to_delete = []

    for time_entry in time_entries(date, project_id):
        if time_entry['task_assignment']['id'] in found_task_assignments:
            entries_to_delete.append(time_entry['id'])

    LOGGER.debug('Entries to delete %s', entries_to_delete)

    for entry in entries_to_delete:
        if not harvest.delete_time_entry(entry):
            LOGGER.error(f'ERROR deleting time entry: %s', entry)
