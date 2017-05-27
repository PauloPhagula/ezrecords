# coding: utf-8
from __future__ import unicode_literals, print_function, absolute_import, with_statement
import sys

PY_MAJOR = sys.version_info[0]
PY_MINOR = sys.version_info[1]
PY2 = PY_MAJOR == 2
PY3 = PY_MAJOR >= 3

if PY2:
    text_type = unicode
    bytes_type = binary_type = str
    string_types = basestring  # (str, unicode)
    integer_types = (int, long)
    numeric_types = (int, long, float)
    from urlparse import parse_qsl
    from decimal import Decimal
    from urllib import quote, unquote, urlencode
    from urlparse import urlparse, urlunparse, urljoin, urlsplit, parse_qsl
elif PY3:
    text_type = str
    bytes_type = binary_type = bytes
    string_types = (str,)
    integer_types = (int,)
    numeric_types = (int, float)
    from urllib.parse import parse_qsl
    from decimal import Decimal
    from urllib.parse import urlparse, urlunparse, urljoin, urlsplit, urlencode, quote, unquote, parse_qsl
