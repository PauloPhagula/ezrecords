# coding: utf-8
from __future__ import absolute_import, print_function, unicode_literals, with_statement

import sys

PY_MAJOR = sys.version_info[0]
PY_MINOR = sys.version_info[1]
PY2 = PY_MAJOR == 2
PY3 = PY_MAJOR >= 3

text_type = str
bytes_type = binary_type = bytes
string_types = (str,)
integer_types = (int,)
numeric_types = (int, float)
from decimal import Decimal
from urllib.parse import (
  parse_qsl,
  quote,
  unquote,
  urlencode,
  urljoin,
  urlparse,
  urlsplit,
  urlunparse,
)
