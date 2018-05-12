# coding: utf-8
"""
SQLite implementation

https://speakerdeck.com/pycon2016/dave-sawyer-sqlite-gotchas-and-gimmes
https://speakerdeck.com/eueung/python-sqlite
"""
import sqlite3
import warnings
from ezrecords.abstractdb import Database


class SQLiteDb(Database):

    def __init__(self, db_url=None, logger=None):
        super(SQLiteDb, self).__init__(db_url=db_url, logger=logger)
        self._placeholder = '?'

    def _connect(self):
        if self._connection is None:
            self._connection = sqlite3.connect(
                self._database,
                check_same_thread=False, # allows us to use multiple threads on the same connection
                isolation_level='DEFERRED' # so we can control transactions
            )

            def _make_dicts(cursor, row):
                return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))
            # self._connection.row_factory = sqlite3.Row
            self._connection.row_factory = _make_dicts

            # This might be pointless once created with an encoding one cannot switch it
            self._connection.execute('PRAGMA encoding = "UTF-8"')

            self._connection.execute('PRAGMA foreign_keys = ON')

            # Requires SQLite 3.7.0 (Jul 2010)
            self._connection.execute('PRAGMA journal_mode = WAL')
            self._connection.execute('PRAGMA temp_store = MEMORY')
            self._connection.execute('PRAGMA synchronous = OFF')

    def _set_charset(self, charset, collate=None):
        # This might be pointless once created with an encoding one cannot switch it
        valid_encodings = ["UTF-8", "UTF-16", "UTF-16le", "UTF-16be"]
        if charset not in valid_encodings:
            raise ValueError('charset')
        self.query('PRAGMA encoding = "%s"' % charset)

    def _db_version(self):
        sql = 'SELECT sqlite_version() as version'
        row = self.query_one(sql)
        version = row['version']
        return version

    def use(self, db_name):
        """select a new database to work with"""
        raise NotImplementedError('Dynamic db switching not allowed in SQLite')

    def exists(self, name, kind='table', schema='public'):
        rv = self.query_one("SELECT exists(SELECT name FROM sqlite_master WHERE type='table' AND name=?) as it_exists", name)
        return bool(rv['it_exists'])

    def _get_table_names(self):
        return self.query('SELECT tbl_name as "table" FROM sqlite_master')

