ezrecords: SQL for Humans™ Enhanced
====================================

.. image:: https://img.shields.io/github/release/dareenzo/ezrecords.svg
    :target: https://github.com/dareenzo/ezrecords/releases
    :alt: Latest Version

.. image:: https://travis-ci.org/dareenzo/ezrecords.svg?branch=master
    :target: https://travis-ci.org/dareenzo/ezrecords
    :alt: Build

.. image:: https://coveralls.io/repos/github/dareenzo/ezrecords/badge.svg?branch=master
    :target: https://coveralls.io/github/dareenzo/ezrecords?branch=master
    :alt: Coverage

.. image:: https://img.shields.io/github/license/dareenzo/ezrecords.svg
    :target: https://github.com/dareenzo/ezrecords/blob/master/LICENSE
    :alt: License

.. _LICENSE: http://www.github.com/dareenzo/ezrecords/blob/master/LICENSE
.. _records: https://github.com/kennethreitz/records
.. _ezsql: https://github.com/ezSQL/ezSQL
.. _wpdb: https://codex.wordpress.org/Class_Reference/wpdb
.. _SQLAlchemy: http://www.sqlalchemy.org


**ezrecords is a very simple, but powerful, library for making raw SQL
queries to most relational databases.**

ezrecords = Kenneth Reitz's `records`_ + Justin Vincent's `ezsql`_ + WordPress' `wpdb`_ - `SQLAlchemy`_.

Just write SQL. No bells, no whistles. This common task can be
surprisingly difficult with the standard tools available.
This library strives to make this workflow as simple as possible,
while providing an elegant interface to work with your query results.

*Database support includes Postgres, MySQL (drivers not included).*

Why?
----

- `records`_ is awesome
- `ezsql`_ and `wpdb`_ have very nice API, so it makes for an easy transition
  from PHP to Python
- Our love for crafting well written and performant SQL queries is not questionable,
  but I think a few helpers for some basic DML and recurring queries would help
- *"The ORM takes two brilliant ideas and incapacitates them both."*,
  said a very wise man. So, as long as possible I want to keep away from
  sqlalchemy or the like.

Usage
------

API
~~~

.. code:: Python

    import logging
    from ezrecords.mysqldb import MySQLDb

    logger = logging.getLogger()

    # connect
    db = MySQLDb(db_url="mysql://root:passwd@127.0.0.1:3306/test", logger=logger) # logger is optional

    # enable debugging - optional
    db.save_queries = True  # save queries and execution time
    db.show_sql = True  # show SQL code being executed. logger above is required for logging to work
    db.show_errors = True  # show errors

    create_user_table = """
    CREATE TABLE test_user (
        id INT AUTO_INCREMENT NOT NULL,
        username varchar(255) UNIQUE,
        password varchar(255),
        created_at TIMESTAMP,
        created_at_gmt TIMESTAMP,
        PRIMARY KEY(id)
    )
    """
    db.query(create_table) # run generic SQL

    create_numbers_table = """
    DROP TABLE IF EXISTS numbers;
    CREATE TABLE numbers(
        ints int,
        floats float
    );
    """
    db.query(create_table_sql)

    insert_numbers_sql = "INSERT INTO numbers (ints, floats) VALUES (%d, %f)" # DB API only accepts %s, so we replace %d and %f by %s internally
    db.query(insert_numbers_sql, 3, 3.14) # run generic queries with params

    # insert records
    db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
    db.insert('test_user', {'username': 'JONES', 'password': 'STEEL'})

    # bulk_insert records
    db.bulk_insert('test_user', ('username', 'password'), [('scott', 'tiger'), ('JONES', 'STEEL')])

    # Update records
    db.update('test_user', {'password': 'shepard'}, {'username': 'scott'})

    # Delete records
    db.delete('test_user', {'username': None}) # None is converted to NULL

    # Sanitize query
    db.prepare("""INSERT INTO postmeta (post_id, meta_key, meta_value) VALUES ( '%d', "%s", %%s )')""", 10, "Harriet's Adages", "WordPress' database interface is like Sunday Morning: Easy.")

    # Call stored procedures
    db.call_procedure('adds', 1, 2)

    # Get single variable/value
    db.get_var('SELECT version()')

    # Get specific row from many results
    db.get_row('SELECT * FROM test_user', row_offset=1) # if offset not given the first row is returned

    # Get specific column from many results
    db.get_col('SELECT username, password FROM test_user', column_offset='password')  # offset can be numeric too

    # Get results in specific format
    db.get_results('SELECT username, password FROM test_user', 'json')
    # Get last inserted ID from AUTO_INCREMENT/SERIAL fields
    db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
    db.last_insert_id

    # Get number of affected rows from previus query
    db.delete('test_user')
    db.affected_rows

    # Switch to another database
    db.use('information_schema')

    # Check query timing
    # execute long running query
    db.last_query_elapsed_time

    # Transactions
    # ---
    db.begin_transaction()
    db.commit() # or db.rollback()

    # Data export
    rows = db.query('SELECT * FROM table')
    rows.dataset
    rows.export('csv') # yaml, json, xls, xlsx

    # Goodies
    db.db_version() # get server version
    db.exists('table') # check if table exists
    db.get_table_names() # get list of tables in database
    db.flush() # clear cache results


CLI
~~~

.. code:: bash

    ezrecords -h
    ezrecords "SELECT version() AS version" "json" --url="mysql://root:passwd@127.0.0.1:3306/test"
    ezrecords "SELECT version() AS version" "json" --url="postgres://postgres:passwd@127.0.0.1:5432/test"
    ezrecords "SELECT sqlite_version() AS version" "json" --url="sqlite:///:memory:"

Thank you
----------
Thanks for checking this library out! I hope you find it useful.

Of course, there's always room for improvement. Feel free to
`open an issue <https://github.com/dareenzo/ezrecords/issues>`_
so we can make **ezrecords** better, faster, and stronger.

Download and Install
--------------------

Until the module is made available on pypi, you can install this module
directly from github with:

``pip install -e git+https://github.com/dareenzo/ezrecords@master#egg=ezrecords``

ezrecords runs with **Python 2.7 and 3.5**.

Documentation Generation
------------------------

.. code-block:: sh

    # edit documentation in _docs
    cd _docs
    make singlehtml
    cd ..
    cp -fR _docs/_build/singlehtml/* docs/


Copyright & License
--------------------

Code and documentation are available according to the MIT License.

See the `LICENSE`_ file for details.
