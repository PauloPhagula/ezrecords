# coding: utf-8
from __future__ import unicode_literals, print_function, absolute_import, with_statement

import os
import unittest
import datetime
import logging

from ezrecords.postgresdb import PostgresDb


class PostgresDbTests(unittest.TestCase):

    def setUp(self):
        dsn = os.getenv('DATABASE_URL', "postgres://postgres@127.0.0.1:5432/test")
        logger = logging.getLogger()
        self.db = PostgresDb(db_url=dsn, logger=logger)

        self.db.save_queries = True
        self.db.show_sql = True
        self.db.show_errors = True

        create_table = """
CREATE TABLE test_user (
    id SERIAL,
    username varchar(255) UNIQUE,
    password varchar(255),
    created_at TIMESTAMP,
    PRIMARY KEY(id)
)
        """
        self.db.query(create_table)

    def tearDown(self):
        self.db.query("DROP TABLE IF EXISTS test_user")
        self.db.close()

    def test_gets_db_engine_version(self):
        self.db.show_sql = True
        db_version = self.db.db_version()
        self.assertTrue(db_version.startswith('9'))

    def test_cannot_change_databases(self):
        # \c is not part of SQL, but of Postgres' CLI
        with self.assertRaises(Exception):
            self.db.use('some_db');

    def test_get_table_names_returns_list_of_tables(self):
        rows = self.db.get_table_names()
        self.assertIn('test_user', map(lambda x: x.table, rows))

    def test_can_check_for_table_existence(self):
        self.assertTrue(self.db.exists('test_user'))
        self.assertFalse(self.db.exists('non_existing_table'))

    def test_cannot_switch_charset(self):
        with self.assertRaises(Exception):
            self.db.set_charset('unknown_charset')

    def test_supports_unicode(self):
        unicode_str = 'unicode string with accents: á, emojis: 🎉 and kanjis 漢字'
        self.db.insert('test_user', {'username': unicode_str, 'password': 'secret'})
        row = self.db.query_one('SELECT * FROM test_user')
        self.assertEqual(unicode_str, row['username'])

    def test_can_call_stored_procedures(self):
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
