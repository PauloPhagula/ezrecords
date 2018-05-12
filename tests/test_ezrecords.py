# coding: utf-8
from __future__ import unicode_literals, print_function, absolute_import, with_statement

import os
import unittest
import datetime
import logging

from ezrecords.mysqldb import MySQLDb


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        dsn = os.getenv('DATABASE_URL', "mysql+pymysql://root@127.0.0.1:3306/test")
        logger = logging.getLogger()
        self.db = MySQLDb(db_url=dsn, logger=logger)

        self.db.save_queries = True
        self.db.show_sql = True
        self.db.show_errors = True

        self.handles = {
            'mysql': '',
            'sqlite': '',
            'postgres': '',
        }

    def tearDown(self):
        pass

