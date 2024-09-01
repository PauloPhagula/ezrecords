# coding: utf-8
"""
SQLite implementation

https://speakerdeck.com/pycon2016/dave-sawyer-sqlite-gotchas-and-gimmes
https://speakerdeck.com/eueung/python-sqlite
"""
import sqlite3
import warnings
import datetime

from ezrecords.abstractdb import Database

def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()

def adapt_datetime_iso(val):
    """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
    return val.isoformat()

def adapt_datetime_epoch(val):
    """Adapt datetime.datetime to Unix timestamp."""
    return int(val.timestamp())

sqlite3.register_adapter(datetime.date, adapt_date_iso)
sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)
sqlite3.register_adapter(datetime.datetime, adapt_datetime_epoch)

def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val.decode())

def convert_datetime(val):
    """Convert ISO 8601 datetime to datetime.datetime object."""
    return datetime.datetime.fromisoformat(val.decode())

def convert_timestamp(val):
    """Convert Unix epoch timestamp to datetime.datetime object."""
    return datetime.datetime.fromtimestamp(int(val))

sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("datetime", convert_datetime)
sqlite3.register_converter("timestamp", convert_timestamp)

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
