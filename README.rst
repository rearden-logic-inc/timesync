Time Sync
=========

Tool that will sync the time record values between `Harvest API v2 <https://help.getharvest.com/api-v2/>`_ and `T-Sheets API V1 <https://developers.tsheets.com/docs/api/>`_.

Installation
------------

.. code-block:: bash

  # Create new virtual environment
  python3 -m venv env

  # Activate Virtual environment
  source env/bin/activate

  # Install timesync application
  pip install git+https://github.com/rearden-logic-inc/timesync.git@master

Configuration
-------------

The application takes a configuration file that will provide the necessary tokens required to connect to the Harvest and T-Sheets APIs.

T-Sheets Notes
~~~~~~~~~~~~~~

This will require installing the API add-on and creating a new application for the admin of the t-sheet instance.  None of the information that is provided for creating a new application matters, it's just required in order to add a new token.  Once the application is created, add a new token for each of the users that will be using the application.

Harvest Notes
~~~~~~~~~~~~~

Configuration details for the harvest API, requires a ``token`` and ``account_id`` which can be found once you are logged into the harvest application.  Instructions can be found in the `API Authentication Instructions <https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#personal-access-tokens>`_.

Configuration File
~~~~~~~~~~~~~~~~~~

The configuration of the API tokens is located in a YAML file.  By default the file ``config.yaml`` is used.  It has the following format.

.. code-block:: yaml

  connections:

    # Configuration details for the harvest API
    harvest:
      account_id: <Your Account ID>
      token: <Your Token>

    # Configuration details for the T-Sheets API
    t-sheets:
      token: <Your Token>

  timeentries:

    # Start time in 24 hour time.  This value is used to generate a start time
    # if there is not a start time provided.
    default_start_time: '08:00:00'

Execution
---------

There are two different executions modes in TimeSync.

Common Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-h
  Help information from the application

-c CONFIG_FILE, --config=CONFIG_FILE
  Specify an alternate configuration file for the application

Task Assignment
~~~~~~~~~~~~~~~

The task assignment subcommand provides a list of all of the project id and task ids for harvest or the Job Codes for T-Sheets.  This information can then be used to configure the process.yaml that is used when copying the data.

.. code-block:: bash

  # Fetch the project and task ids from harvest
  timesync task_assignments harvest

  # Fetch the jobcodes from T-sheets
  timesync task_assignments tsheets

Both commands will provide a tabular output containing human readable names and the integer codes associated with each.

Process
~~~~~~~

The process command takes a single argument that is a script file containing instructions.  Currently the only commands are ``copy`` (which will copy the values from a reader and writes them to a writer) and ``delete`` (which will delete the time entries for a specified task/jobcode).

.. code-block:: bash

  timesync process process.yaml

Example Process File
####################

.. code-block:: yaml

  tasks:

  # Tasks are executed in order that they are defined in this file, currently
  # available tasks are 'delete', and 'copy'.  The delete command is provided
  # so that values that may have been copied before are removed before copying
  # values over.  If this is not required, then remove/comment out the task.

  - type: delete
    # Delete task will remove all of the values from the harvest project/task
    # or the tsheets jobcode.
    from:

      # Required field that defines which API to use.   Currently only harvest
      # deleter is supported.
      id: harvest

      # The following are required fields if the id is set to 'harvest'.  These
      # values can be retrieved from the output of the task_assignment
      # subcommand
      project: 1
      task: 2

    # Date that time entries will be deleted.  This value can be: 'today',
    # 'yesterday', 'range', or 'YYYY-MM-DD' value.  If 'range' is specified
    # then additional fields 'start' and 'end' must also be defined.
    date: today
    # start: '2019-01-01'
    # end: '2019-01-30'

  - type: copy
    # Copies the values from one API to another API.

    from:

      # Required field that defines the API to use for reading.  Currently
      # only tsheets or disk reader is supported.
      id: tsheets

      # Required field if the id is set to tsheets.  This value can be
      # retrieved from the output of the task_assignment subcommand.
      jobcode: 34

      # Required field if the id is set to disk.
      # filename: some_file.yaml

    to:

      # Required field that defines the API to use for writing.  Currently only
      # harvest or disk writer is supported.
      id: harvest

      # See documentation on these fields provided in the delete section.
      project: 1
      task: 2

      # Required field if the id is set to disk.
      # filename: some_file.yaml

    # See the documentation on these fields provided in the delete section.
    date: today
    # start: '2019-01-01'
    # end: '2019-01-30'

Limitations
-----------

This application is currently under development and has the following limitations:

* Can only read time entry values from the T-Sheets API or from YAML formatted file
* Can only write time entry values to the Harvest API or to YAML formatted file
* Can only delete time entry values from the Harvest API
