# Change log

For a complete view of all the releases, visit the releases page on GitHub:
[https://github.com/dareenzo/ezrecords/releases](https://github.com/dareenzo/ezrecords/releases)

## v0.2.0 - 2017-05-27

Features:

- Bulk insert: `db.bulk_insert('test_user', ('username', 'password'), [('scott', 'tiger'), ('JONES', 'STEEL')])`

Fixes:

- Improve documentation
- Update base records library code
- Fixes error with getting passing params to query
- start unquoting username and password as defined in the standard RFC

## v0.1.0 - 2017-01-07

- Initial release
