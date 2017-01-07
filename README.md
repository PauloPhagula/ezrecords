# ezrecords - SQL for the enhanced

## What?

ezrecords = Kenneth Reitz's records + Justin Vincent's ezsql/wpdb - SQLAlchemy.

A very simple, but powerful, library for making raw SQL queries to most
relational databases.

Just write SQL. No bells, no whistles. This common task can be
surprisingly difficult with the standard tools available. This library
strives to make this workflow as simple as possible, while providing an
elegant interface to work with your query results.

Database support includes Postgres, MySQL.

## Why?

- Records is awesome
- ezsql/wpdb is good and I'm used to it's API, so it makes for an easy transition from PHP to Python
- Our love for crafting well written and performant SQL queries is not questionable, but I think a few helpers for some basic DML and recurring queries would help
- "ORM takes two great ideas and destroys them both.", said a very wise man. So as long as possible I want to keep away from sqlalchemy or the like.

## Usage

### API

```python
import logging
from ezrecords.mysqldb import MySQLDb

# connect
logger = logging.getLogger()
db = MySQLDb(db_url=dsn, logger=logger) # logger is optional

# enable debugging - optional
db.save_queries = True  # save queries and execution time
db.show_sql = True  # show SQL code being executed
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
get_row('SELECT * FROM test_user', row_offset=1) # if offset not given the first row is returned

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
```

### CLI

```sh
ezrecords -h
ezrecords "SELECT version() AS version" "json" --url="mysql://root:passwd@127.0.0.1:3306/test"
ezrecords "SELECT version() AS version" "json" --url="postgres://postgres:passwd@127.0.0.1:5432/test"
```

## Thank you

Thanks for checking this library out! I hope you find it useful.

Of course, there's always room for improvement. Feel free to
[open an issue](/issues) so we can make **ezrecords** better, stronger,
faster.
