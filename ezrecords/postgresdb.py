# coding: utf-8
import psycopg2
import psycopg2.extras
import psycopg2.extensions

from ezrecords.abstractdb import Database

# My database is Unicode, but I receive all strings as UTF-8 `str`.
# Can I receive unicode `objects` instead?
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


class PostgresDb(Database):

    def __init__(self, db_url=None, logger=None):
        super(PostgresDb, self).__init__(db_url=db_url, logger=logger)

    def _connect(self):
        # Psycopg automatically converts Postgres JSON data into Python objects.
        # How can I receive strings instead?
        # psycopg2.extras.register_default_json(loads=lambda x: x)  # if enabled PQ stops working

        if self._connection is None:
            self._connection = psycopg2.connect(
                dbname=self._database,
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port,
                cursor_factory=psycopg2.extras.DictCursor
            )

            # psycopg2 starts a new transaction on connection opening by default,
            # that means we have to commit after every statement and we don't want that.
            # if I want a transaction I'll start by hand.
            self._connection.rollback()  # rollback implicit transaction first. http://stackoverflow.com/questions/39028663/unable-to-set-psycopg2-autocommit-after-shp2pgsql-import
            self._connection.autocommit = True

            # READCOMMITED
            # self._connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
            # self._connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            # self.set_charset('utf8')

    def _set_charset(self, charset, collate=None):
        sql = 'SET NAMES %s'
        self.query(sql, charset)

    def _db_version(self):
        rv = self.get_var("SELECT split_part(ltrim(version(), 'PostgreSQL '), ' ', 1) as server_version;")
        return rv

    def use(self, db_name):
        """select a new database to work with"""
        raise NotImplementedError('Dynamic db switching not allowed in Postgres')

    def exists(self, name, kind='table', schema='public'):
        rv = self.query_one("SELECT EXISTS (SELECT relname FROM pg_class WHERE relname=%s)", name)
        return rv['exists']

    def _get_table_names(self):
        sql = """
SELECT table_name as "table"
FROM information_schema.tables
WHERE table_schema='public'
ORDER BY table_name
        """
        return self.query(sql)
