import unittest

from ezrecords.util import parse_db_url

class UtilTest(unittest.TestCase):

    def test_parses_valid_urls(self):
        parse_db_url("mysql://scott:tiger@hostname/dbname")
        parse_db_url("mysql://scott:tiger@hostname:3306/dbname")
        parse_db_url("mysql+pymysql://scott:tiger@hostname:3306/dbname")
        parse_db_url("mysql+pymysql://scott:tiger@hostname:3306/dbname?key=val&key1=val2")
        parse_db_url("mysql+pymysql://scott:tiger@192.168.100.2:3306/dbname?key=val&key1=val2")
        parse_db_url("mysql+pymysql://scott:tiger@fe80::1437:2e9d:f627:ac6d:3306/dbname?key=val&key1=val2")
        parse_db_url("sqlite:///:memory:")  # memory
        parse_db_url("sqlite:///random.db")  # relative
        parse_db_url("sqlite:////random.db")  # absolute
