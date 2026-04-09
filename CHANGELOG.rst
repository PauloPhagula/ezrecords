Change log
==========

For a complete view of all the releases, visit the releases page on
GitHub: https://github.com/PauloPhagula/ezrecords/releases

v1.1.0 / 2026-03-10
-------------------

  * Modernize project's packaging and dependency management with uv (#25)
  * chore(deps): bump tablib from 3.6.1 to 3.9.0 (#26)
  * chore(deps-dev): bump pytest from 8.3.3 to 9.0.2 (#27)
  * chore(deps): bump psycopg2 from 2.9.9 to 2.9.11 (#28)
  * Change changelog format from markdown to rst

v1.0.0 - 2026-03-09
-------------------

Breaking changes:

- Dropped Python 2 support, while maintaining compatibility only with
  maintained Python 3 versions

v0.3.0 - 2018-05-12
-------------------

Features:

- Added support for SQLite

v0.2.0 - 2017-05-27
-------------------

Features:

- Bulk insert:
  ``db.bulk_insert('test_user', ('username', 'password'), [('scott', 'tiger'), ('JONES', 'STEEL')])``

Fixes:

- Improve documentation
- Update base records library code
- Fixes error with getting passing params to query
- start unquoting username and password as defined in the standard RFC

v0.1.0 - 2017-01-07
-------------------

- Initial release
