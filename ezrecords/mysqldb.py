# coding: utf-8
import os
import pymysql
import pymysql.cursors

from ezrecords.abstractdb import Database


class MySQLDb(Database):

    def __init__(self, db_url=None, logger=None):
        super(MySQLDb, self).__init__(db_url=db_url, logger=logger)

    def _connect(self):
        if self._connection is None:
            '''
            don't set "use_unicode=0"
            SQLAlchemy people say don't set this at all
            http://docs.sqlalchemy.org/en/latest/dialects/mysql.html
            '''

            DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')
            DB_COLLATION = os.getenv('DB_COLLATION', 'utf8mb4_general_ci')
            DB_SQL_MODE = os.getenv('DB_SQL_MODE', "'ANSI,STRICT_TRANS_TABLES,STRICT_ALL_TABLES,ONLY_FULL_GROUP_BY'")
            DB_TIMEZONE = os.getenv('DB_TIMEZONE', "'+2:00'")

            self._connection = pymysql.connect(
                host=self._host,
                user=self._user,
                passwd=self._password,
                database=self._database,
                port=self._port,
                charset=DB_CHARSET,
                cursorclass=pymysql.cursors.DictCursor,
                # persistent
            )

            # Force MySQL to UTF-8 Encodingclear
            self.set_charset(DB_CHARSET, DB_COLLATION)
            # self.query("SET NAMES %s COLLATE %s" % (DB_CHARSET, DB_COLLATION))
            # self.query("SET CHARACTER_SET_RESULTS='%s'" % DB_CHARSET)

            # Default MySQL behavior to conform more closely to SQL standards.
            # This allows to run almost seamlessly on many different kinds of database systems.
            # These settings force MySQL to behave the same as postgresql, or sqlite
            # in regards to syntax interpretation and invalid data handling. See
            # https://www.drupal.org/node/344575 for further discussion. Also, as MySQL
            # 5.5 changed the meaning of TRADITIONAL we need to spell out the modes one by one
            self.query("SET SESSION sql_mode = %s" % DB_SQL_MODE)  # Force MySQL ANSI compatibilities

            self.query("SET SESSION time_zone = %s" % DB_TIMEZONE)

    def _set_charset(self, charset, collate=None):
        sql = 'SET NAMES %s' % charset

        if collate is not None:
            sql += ' COLLATE %s' % collate

        self.query(sql)
        self.query('SET CHARACTER_SET_RESULTS=%s', charset)

    def _db_version(self):
        sql = 'SELECT version() as version'
        row = self.query_one(sql)
        version = row['version']
        return version

    def use(self, db_name):
        """Selects a new database to work with"""
        self._connection.select_db(db_name)

    def exists(self, name, kind='table', schema='public'):
        rv = self.query_one("SELECT EXISTS ()", name)
        return rv['exists']

    def set_sql_mode(self, modes):
        """Changes the current SQL mode.

        Args:
            modes (list): A list of SQL modes to set
        """
        if len(modes) == 0:
            return

        modes = map(lambda x: x.upper())
        modes_str = ', '.join(modes)
        self.query('SET SESSION sql_mode = %s', modes_str)
        self._sql_mode = modes_str

    def _get_table_names(self):
        sql = """
SELECT table_name AS "table" -- , ROUND(((data_length + index_length) / 1024 / 1024), 2) "size_in_mb"
  FROM information_schema.TABLES
  WHERE table_schema = database()
  ORDER BY 1 -- (data_length + index_length) DESC
        """
        return self.query(sql)
