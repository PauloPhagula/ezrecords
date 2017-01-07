# coding: utf-8
from __future__ import unicode_literals, print_function, absolute_import, with_statement

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from docopt import docopt

from ezrecords.mysqldb import MySQLDb
from ezrecords.postgresdb import PostgresDb
from ezrecords.util import parse_db_url


def cli():
    cli_docs = """Records: SQL for Humans™
A Kenneth Reitz project.
Usage:
  records <query> <format> [<params>...] [--url=<url>]
  records (-h | --help)
Options:
  -h --help     Show this screen.
  --url=<url>   The database URL to use. Defaults to $DATABASE_URL.
Supported Formats:
   csv, tsv, json, yaml, html, xls, xlsx, dbf, latex, ods
   Note: xls, xlsx, dbf, and ods formats are binary, and should only be
         used with redirected output e.g. '$ records sql xls > sql.xls'.
Query Parameters:
    Query parameters can be specified in key=value format, and injected
    into your query in :key format e.g.:
    $ records 'select * from repos where language ~= :lang' lang=python
Notes:
  - While you may specify a database connection string with --url, records
    will automatically default to the value of $DATABASE_URL, if available.
  - Query is intended to be the path of a SQL file, however a query string
    can be provided instead. Use this feature discernfully; it's dangerous.
  - Records is intended for report-style exports of database queries, and
    has not yet been optimized for extremely large data dumps.
    """
    supported_formats = 'csv tsv json yaml html xls xlsx dbf latex ods'.split()

    # Parse the command-line arguments.
    arguments = docopt(cli_docs)

    # Create the Database.
    dsn_components = parse_db_url(arguments['--url'])
    db = None
    if dsn_components['dialect'] == 'mysql':
        db = MySQLDb(arguments['--url'])

    if dsn_components['dialect'] == 'postgres':
        db = PostgresDb(arguments['--url'])

    assert db is not None

    query = arguments['<query>']
    params = arguments['<params>']

    # Can't send an empty list if params aren't expected.
    try:
        params = dict([i.split('=') for i in params])
    except ValueError:
        print('Parameters must be given in key=value format.')
        exit(64)

    # Execute the query, if it is a found file.
    if os.path.isfile(query):
        rows = db.query_file(query, **params)

    # Execute the query, if it appears to be a query string.
    elif len(query.split()) > 2:
        rows = db.query(query, **params)

    # Otherwise, say the file wasn't found.
    else:
        print('The given query could not be found.')
        exit(66)

    # Print results in desired format.
    if arguments['<format>']:
        print(rows.export(arguments['<format>']))
    else:
        print(rows.dataset)

# Run the CLI when executed directly.
if __name__ == '__main__':
    cli()
