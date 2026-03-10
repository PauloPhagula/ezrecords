# coding: utf-8
from __future__ import unicode_literals, print_function, absolute_import, with_statement

import os
import unittest
import datetime
import logging

from ezrecords.sqlitedb import SQLiteDb

class SQLiteDbTests(unittest.TestCase):

    def setUp(self):
        dsn = "sqlite:///:memory:"
        logger = logging.getLogger()
        self.db = SQLiteDb(db_url=dsn, logger=logger)

        self.db.save_queries = True
        self.db.show_sql = True
        self.db.show_errors = True

        # Avoid using AUTOINCREMENT with SQLite. It imposses imposes extra CPU,
        # memory, disk space, and disk I/O overhead. See https://sqlite.org/autoinc.html
        create_table = """
CREATE TABLE test_user (
    id INTEGER PRIMARY KEY,
    username varchar(191) UNIQUE,
    password varchar(191),
    created_at TIMESTAMP
)
        """
        self.db.query(create_table)

    def tearDown(self):
        self.db.query("DROP TABLE IF EXISTS test_user")
        self.db.close()

    # General / Common
    # ---

    def test_insert(self):
        self.assertEqual(1, self.db.insert('test_user', username='abc', password='secret', created_at=datetime.datetime.now()))
        self.assertEqual(1, self.db.insert('test_user', {'username': 'def', 'password': 'secret'}))

    def test_bulk_insert_works_with_multiple_formats(self):
        columns_as_tuples = ('username', 'password')
        rows_as_tuples_list = [
            ('abc', 'secret'),
            ('def', 'secret')
        ]

        columns_as_list = ['username', 'password']
        rows_as_lists_list = [
            ['ghf', 'secret'],
            ['ijk', 'secret']
        ]

        rows_as_lists_tuple = (
            ('lmn', 'secret'),
            ('opq', 'secret')
        )

        self.assertEqual(2, self.db.bulk_insert('test_user', columns_as_tuples, rows_as_tuples_list))
        self.assertEqual(2, self.db.bulk_insert('test_user', columns_as_list, rows_as_lists_list))
        self.assertEqual(2, self.db.bulk_insert('test_user', columns_as_list, rows_as_lists_tuple))

    def test_update(self):
        self.db.insert('test_user', username='abc', password='secret')
        self.assertEqual(1, self.db.update('test_user', {'password': 'supersecret'}, {'username': 'abc'}))
        self.assertEqual(0, self.db.update('test_user', {'password': 'None'}, {'username': None}))

    def test_delete(self):
        self.db.insert('test_user', username='abc', password='secret')
        self.assertEqual(1, self.db.delete('test_user', {'username': 'abc'}))
        self.assertEqual(0, self.db.delete('test_user', {'username': None}))

    def test_get_var(self):
        var = self.db.get_var('SELECT 1 + 1 as x')
        self.assertEqual(2, var)

    def test_get_row(self):
        self.db.insert('test_user', username='abc', password='secret', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'def', 'password': 'secret'})
        row = self.db.get_row('SELECT * FROM test_user', row_offset=1)
        self.assertEqual(row.username, 'def')

        self.assertTrue(dict, self.db.get_row('SELECT * FROM test_user', output_type='dict'))
        self.assertTrue(dict, self.db.get_row('SELECT * FROM test_user', output_type='object'))

    def test_get_col(self):
        self.db.insert('test_user', username='abc', password='secret', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'def', 'password': 'secret'})
        rows = self.db.get_col('SELECT username, password FROM test_user', column_offset='password')
        self.assertIn('secret', rows)

    def test_injection(self):
        self.db.insert('test_user', username='abc', password='secret')
        self.assertEqual(0, self.db.update('test_user', {'password': 'supersecret'}, {'username': "abc'; DELETE FROM test_user;"}))

    def test_numeric_param_formats_are_parsed(self):
        self.db.query("DROP TABLE IF EXISTS numbers")
        self.db.query("CREATE TABLE numbers(integers int, floats float)")
        self.db.query("INSERT INTO numbers (integers, floats) VALUES (%d, %f)", 3, 3.14)
        self.db.query("DROP TABLE IF EXISTS numbers")

    def test_files_queries_are_executed(self):
        query_file_path = os.path.join(os.path.dirname(__file__), 'sample_query.sql')
        rv = self.db.query_file(query_file_path, one=True)
        self.assertEqual(1, rv['maximum'])

    def test_when_inserting_records_last_auto_increment_value(self):
        self.db.insert('test_user', username='abc', password='secret', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'def', 'password': 'secret'})

        self.assertEqual(2, self.db.last_insert_id)

    def test_records_affected_rows_count(self):
        self.db.insert('test_user', username='abc', password='secret', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'def', 'password': 'secret'})
        self.db.delete('test_user')
        self.assertEqual(2, self.db.affected_rows)

    def test_when_used_saves_query_statements(self):
        self.db.insert('test_user', username='abc', password='secret', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'def', 'password': 'secret'})
        self.assertTrue(self.db.queries_executed >= 2)

    def test_when_flushed_cleans_saved_queries_and_stats(self):
        self.db.insert('test_user', username='abc', password='secret', created_at=datetime.datetime.now())
        self.db.insert('test_user', {'username': 'def', 'password': 'secret'})

        self.assertTrue(self.db.queries_executed >= 2)
        self.assertTrue(len(self.db.saved_queries) > 2)

        self.db.flush()
        self.assertEqual(0, self.db.queries_executed)
        self.assertEqual(0, len(self.db.saved_queries))

    def test_tablib_integration(self):
        self.db.insert('test_user', username='abc', password='secret')
        rows = self.db.query('SELECT * FROM test_user')
        self.assertIsNotNone(rows.dataset)

    # Driver Specific
    # ---

    def test_gets_db_engine_version(self):
        self.db.show_sql = True
        version = self.db.db_version()
        self.assertTrue(version.startswith('3'))

    def test_cannot_change_databases(self):
        with self.assertRaises(Exception):
            self.db.use('some_db');

    def test_get_table_names_returns_list_of_tables(self):
        rows = self.db.get_table_names()
        self.assertIn('test_user', map(lambda x: x.table, rows))

    def test_can_check_for_table_existence(self):
        self.assertTrue(self.db.exists('test_user'))
        self.assertFalse(self.db.exists('non_existing_table'))

    def test_can_switch_to_valid_charsets(self):
        self.db.set_charset('UTF-8')
        self.db.set_charset('UTF-16')
        self.db.set_charset('UTF-16le')
        self.db.set_charset('UTF-16be')

        with self.assertRaises(Exception):
            self.db.set_charset('unknown_charset')

    def test_supports_unicode(self):
        unicode_str = 'unicode string with accents: á, emojis: 🎉 and kanjis 漢字'
        self.db.insert('test_user', {'username': unicode_str, 'password': 'secret'})
        row = self.db.query_one('SELECT * FROM test_user')
        self.assertEqual(unicode_str, row['username'])

    def test_cannot_call_stored_procedured(self):
        pass

    def test_transactions(self):
        self.db.begin_transaction()
        self.db.insert('test_user', {'username': 'x', 'password': 'secret'})
        self.db.insert('test_user', {'username': 'y', 'password': 'secret'})
        self.db.rollback()
        self.assertEqual(0, self.db.get_var("SELECT count(*) as x FROM test_user"))

        self.db.begin_transaction()
        self.db.insert('test_user', {'username': 'z', 'password': 'secret'})
        self.db.commit()
        self.assertEqual(1, self.db.get_var("SELECT count(*) as x FROM test_user"))

    def test_warns_for_multiple_statements(self):
        pass
