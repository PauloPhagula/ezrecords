# coding: utf-8
from __future__ import unicode_literals, print_function, absolute_import, with_statement

import os
import unittest
import datetime
import logging

from ezrecords.mysqldb import MySQLDb
from ezrecords.postgresdb import PostgresDb
from ezrecords.util import parse_db_url

class MySQLDbTests(unittest.TestCase):

    def setUp(self):
        dsn = os.getenv('DATABASE_URL', "mysql+pymysql://root@127.0.0.1:3306/test")
        logger = logging.getLogger()
        self.db = MySQLDb(db_url=dsn, logger=logger)
        self.db.save_queries = True
        self.db.show_sql = True
        self.db.show_errors = True
        create_table = """
CREATE TABLE test_user (
    id INT AUTO_INCREMENT NOT NULL,
    username varchar(255) UNIQUE,
    password varchar(255),
    created_at TIMESTAMP,
    created_at_gmt TIMESTAMP,
    PRIMARY KEY(id)
)
        """
        self.db.query(create_table)

    def tearDown(self):
        drop_table = """DROP TABLE test_user"""
        self.db.query(drop_table)
        self.db.close()

    def test_db_version(self):
        self.db.show_sql = True
        db_version = self.db.db_version()
        self.assertIsNotNone(db_version)
        self.assertTrue(db_version.startswith('5'))

    def test_insert(self):
        self.db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'JONES', 'password': 'STEEL'})

    def test_update(self):
        self.db.insert('test_user', username='scott', password='tiger')
        self.db.update('test_user', {'password': 'shepard'}, {'username': 'scott'})
        self.db.update('test_user', {'password': 'None'}, {'username': None})

    def test_delete(self):
        self.db.insert('test_user', username='scott', password='tiger')
        self.db.delete('test_user', {'username': 'scott'})
        self.db.delete('test_user', {'username': None})

    def test_injection(self):
        self.db.insert('test_user', username='scott', password='tiger')
        self.db.update('test_user', {'password': 'shepard'}, {'username': "scott'; DELETE FROM test_user;"})

    def test_numeric_param_formats_are_parsed(self):
        create_table_sql = """
DROP TABLE IF EXISTS numbers;
CREATE TABLE numbers(
    ints int,
    floats float
);
        """
        insert_numbers_sql = "INSERT INTO numbers (ints, floats) VALUES (%d, %f)"
        self.db.query(create_table_sql)
        self.db.query(insert_numbers_sql, 3, 3.14)
        self.db.query('drop table numbers')

    def test_prepare_sanitizes_string(self):
        sql = self.db.prepare("""INSERT INTO postmeta (post_id, meta_key, meta_value) VALUES ( '%d', "%s", %%s )')""", 10, "Harriet's Adages", "WordPress' database interface is like Sunday Morning: Easy.")
        self.assertEqual(-1, sql.find('%'))

    def test_db_unicode_support(self):
        create_sql = """
DROP TABLE IF EXISTS poo;

CREATE TABLE poo(contents varchar(191));

INSERT INTO poo(contents) VALUES ('big ol pile of 💩');
        """
        self.db.query(create_sql)

        row = self.db.query_one('SELECT * FROM poo')

        self.assertEqual('big ol pile of 💩', row['contents'])

    def test_stored_procs_are_called(self):
        # DELIMITER is not part of SQL. It' part of mysql command line tool
        # so we must not use
        create_proc_sql = """
-- DELIMITER //

DROP PROCEDURE IF EXISTS adds;

CREATE PROCEDURE adds(IN a int, IN b int)
BEGIN
    SELECT a + b;
END;

-- DELIMITER ;
        """
        self.db.query(create_proc_sql)
        rv = self.db.call_procedure('adds', 1, 2)
        self.assertEqual(3, rv[0]['a + b'])

    def test_files_queries_are_executed(self):

        query_file_path = os.path.join(os.path.dirname(__file__), 'sample_query.sql')
        rv = self.db.query_file(query_file_path, one=True)
        self.assertEqual('test', rv['database'])

    def test_tab_lib_integration(self):
        self.db.insert('test_user', username='scott', password='tiger')
        rows = self.db.query('SELECT * FROM test_user')
        self.assertIsNotNone(rows.dataset)

    def test_get_table_names_returns_list_of_tables(self):
        rows = self.db.get_table_names()
        self.assertIn('test_user', map(lambda x: x.table, rows))

    def test_get_var(self):
        version = self.db.get_var('SELECT version()')
        self.assertTrue(version.startswith('5'))

    def test_get_row(self):
        self.db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'JONES', 'password': 'STEEL'})
        row = self.db.get_row('SELECT * FROM test_user', row_offset=1)
        self.assertEqual(row.username, 'JONES')

        self.assertTrue(dict, self.db.get_row('SELECT * FROM test_user', output_type='dict'))
        self.assertTrue(dict, self.db.get_row('SELECT * FROM test_user', output_type='object'))

    def test_get_col(self):
        self.db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'JONES', 'password': 'STEEL'})
        rows = self.db.get_col('SELECT username, password FROM test_user', column_offset='password')
        self.assertIn('STEEL', rows)

    def test_parse_db_url(self):
        parse_db_url("mysql://scott:tiger@hostname/dbname")
        parse_db_url("mysql://scott:tiger@hostname:3306/dbname")
        parse_db_url("mysql+pymysql://scott:tiger@hostname:3306/dbname")
        parse_db_url("mysql+pymysql://scott:tiger@hostname:3306/dbname?key=val&key1=val2")
        parse_db_url("mysql+pymysql://scott:tiger@192.168.100.2:3306/dbname?key=val&key1=val2")
        parse_db_url("mysql+pymysql://scott:tiger@fe80::1437:2e9d:f627:ac6d:3306/dbname?key=val&key1=val2")
        parse_db_url("sqlite:///:memory:")  # memory
        parse_db_url("sqlite:///random.db")  # relative
        parse_db_url("sqlite:////random.db")  # absolute

    def test_last_auto_increment_value_is_recorded_on_insert(self):
        self.db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'JONES', 'password': 'STEEL'})

        self.assertEqual(2, self.db.last_insert_id)

    def test_affected_rows_count_is_recorded(self):
        self.db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'JONES', 'password': 'STEEL'})
        self.db.delete('test_user')
        self.assertEqual(2, self.db.affected_rows)

    def test_use_should_change_database(self):
        self.db.use('information_schema')
        using_db = self.db.get_var('SELECT database()')
        self.assertEqual('information_schema', using_db)
        self.db.use('test')

    def test_queries_are_saved(self):
        self.db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'JONES', 'password': 'STEEL'})
        self.assertTrue(self.db.queries_executed >= 2)

    def test_flush_should_clean_saved_queries_and_stats(self):
        self.db.insert('test_user', username='scott', password='tiger', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'JONES', 'password': 'STEEL'})

        self.assertTrue(self.db.queries_executed >= 2)
        self.assertTrue(len(self.db.saved_queries) > 2)

        self.db.flush()
        self.assertEqual(0, self.db.queries_executed)
        self.assertEqual(0, len(self.db.saved_queries))


class PostgresDbTests(unittest.TestCase):

    def setUp(self):
        dsn = os.getenv('DATABASE_URL', "postgres://postgres@127.0.0.1:5432/test")
        logger = logging.getLogger()
        self.db = PostgresDb(db_url=dsn, logger=logger)

        create_table = """
CREATE TABLE test_user (
    id SERIAL,
    username varchar(255) UNIQUE,
    password varchar(255),
    created_at TIMESTAMP,
    created_at_gmt TIMESTAMP,
    PRIMARY KEY(id)
)
        """
        self.db.query(create_table)

    def tearDown(self):
        drop_table = """DROP TABLE test_user"""
        self.db.query(drop_table)
        self.db.close()

    def test_stored_procs_are_called(self):
        create_proc_sql = """
    DROP FUNCTION IF EXISTS adds(IN a int, IN b int);

    CREATE FUNCTION adds (integer, integer) RETURNS integer
        AS 'select $1 + $2;'
        LANGUAGE SQL
        IMMUTABLE
        RETURNS NULL ON NULL INPUT;
            """
        self.db.query(create_proc_sql)
        rv = self.db.call_procedure('adds', 1, 2)
        self.assertEqual(3, rv[0][0])


if __name__ == '__main__':
    unittest.main()
