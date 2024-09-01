# coding: utf-8
from __future__ import unicode_literals, print_function, absolute_import, with_statement

import os
import unittest
import datetime
import logging

from ezrecords.mysqldb import MySQLDb


class MySQLDbTests(unittest.TestCase):

    def setUp(self):
        dsn = os.getenv('DATABASE_URL', "mysql+pymysql://root@127.0.0.1:3306/test")
        logger = logging.getLogger()
        self.db = MySQLDb(db_url=dsn, logger=logger)

        self.db.save_queries = True
        self.db.show_sql = True
        self.db.show_errors = True

        create_table = """
CREATE TABLE IF NOT EXISTS test_user (
    id INT AUTO_INCREMENT NOT NULL,
    username varchar(191) UNIQUE,
    password varchar(191),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY(id)
) CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        self.db.query(create_table)

    def tearDown(self):
        self.db.query("DROP TABLE IF EXISTS test_user")
        self.db.close()

    def test_gets_db_engine_version(self):
        self.db.show_sql = True
        db_version = self.db.db_version()
        self.assertTrue(db_version.startswith('9'))

    def test_can_change_database(self):
        self.db.use('information_schema')
        using_db = self.db.get_var('SELECT database()')
        self.assertEqual('information_schema', using_db)
        self.db.use('test') # required for tearDown

    def test_get_table_names_returns_list_of_tables(self):
        rows = self.db.get_table_names()
        self.assertIn('test_user', map(lambda x: x.table, rows))

    def test_can_check_for_table_existence(self):
        self.assertTrue(self.db.exists('test_user'))
        self.assertFalse(self.db.exists('non_existing_table'))

    def test_can_switch_to_valid_charset(self):
        self.db.set_charset('UTF8')

        with self.assertRaises(Exception):
            self.db.set_charset('unknown_charset')

    def test_supports_unicode(self):
        unicode_str = 'unicode string with accents: á, emojis: 🎉 and kanjis 漢字'
        self.db.insert('test_user', {'username': unicode_str, 'password': 'secret'})
        row = self.db.query_one('SELECT * FROM test_user')
        self.assertEqual(unicode_str, row['username'])

    @unittest.skip("Skipping for now")
    def test_can_call_stored_procedures(self):
        # DELIMITER is not part of SQL, but of mysql's CLI tool thus we must not use
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
