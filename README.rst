Time Sync
=========

Tool that will sync the time record values between `Harvest API v2<https://help.getharvest.com/api-v2/>`_ and `T-Sheets API V1<https://developers.tsheets.com/docs/api/>`_.

Installation
------------

.. code-block:: bash

  # Create new virtual environment
  python3 -m venv env

  # Install timesync application
  pip install git+https://<Rest of the URL>

Configuration
-------------

The application takes a configuration file that will provide the necessary tokens required to connect to the Harvest and T-Sheets APIs.

T-Sheets Notes
~~~~~~~~~~~~~~

This will require installing the API add-on and creating a new application for the admin of the t-sheet instance.  None of the information that is provided for creating a new application matters, it's just required in order to add a new token.  Once the application is created, add a new token for each of the users that will be using the application.

Harvest Notes
~~~~~~~~~~~~~

Configuration details for the harvest API, requires a token and account_id which can be found once you are logged into the harvest application.  Instructions can be found in the `API Authentication Instructions<https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#personal-access-tokens>`_.

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

Execution
---------

There are two different executions modes in TimeSync.

Common Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-h
  Help information from the application

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

  TODO: Populate this

Limitations
-----------

This application is currently under development and has the following limitations:

* Can only read time entry values from the T-Sheets API
* Can only write time entry values to the Harvest API
* Can only delete time entry values from the Harvest API
