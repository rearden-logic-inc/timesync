"""
Setup script that installs the packages, configures the plugins, and registers the executables.
"""

from os import path

from setuptools import find_packages, setup

LOCAL_PATH = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(LOCAL_PATH, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='timesync',
    version='0.0.1',
    packages=find_packages(),
    url='',
    license='',
    author='Robert Robinson',
    author_email='rerobins@gmail.com',
    description='Time sheet synchronization tool.',
    long_description=LONG_DESCRIPTION,
    python_requires='>=3.6,<3.8',
    classifiers=[
        'Environment :: Console',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6'
        'Programming Language :: Python :: 3.7',

        'License :: OSI Approved :: Apache Software License',
    ],
    install_requires=[
        'requests==2.21.0',
        'ruamel.yaml>=0.15.70<0.16',
        'tabulate>=0.8.2<0.9',
        'python-dateutil==2.7.5',
    ],

    extras_require={
    },

    setup_requires=[],
    tests_require=[],

    entry_points={
        'console_scripts': ['timesync=timesync.main:main'],

        'task_assignments': ['harvest=timesync.harvest.entries:task_assignments',
                             'tsheets=timesync.tsheets.entries:task_assignments', ],

        'timesheet_reader': ['tsheets=timesync.tsheets.entries:time_entry_reader', ],

        'timesheet_writer': ['harvest=timesync.harvest.entries:time_sheet_writer', ],

        'timesheet_delete': ['harvest=timesync.harvest.entries:time_sheet_delete', ],
    },

    project_urls={
    },
)