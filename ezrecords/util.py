# coding: utf-8
from __future__ import unicode_literals, print_function, absolute_import, with_statement
import re
import datetime

from ezrecords.compat import (
    parse_qsl, PY3, string_types, binary_type, text_type, integer_types,
    Decimal, unquote
)


def preg_replace(pattern, replacement, subject, limit=-1):
    if limit == -1:
        return re.sub(pattern, replacement, subject, flags=re.DOTALL)
    return re.sub(pattern, replacement, subject, limit, flags=re.DOTALL)


def str_replace(search, replace, subject, count=None):
    if count is None:
        return subject.replace(search, replace)
    return subject.replace(search, replace, count)


def format_timedelta(delta, granularity='second', threshold=.85):
    TIME_INTERVALS = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 3600 * 24,
        "week": 3600 * 24 * 7,
        "month": 3600 * 24 * 30,
        "year": 3600 * 24 * 365
    }

    if isinstance(delta, datetime.datetime):
        delta = datetime.datetime.utcnow() - delta
    if isinstance(delta, datetime.timedelta):
        seconds = int((delta.days * 86400) + delta.seconds)
    else:
        seconds = delta

    for unit in TIME_INTERVALS:
        secs_per_unit = TIME_INTERVALS[unit]
        value = abs(seconds) / secs_per_unit
        if value >= threshold or unit == granularity:
            if unit == granularity and value > 0:
                value = max(1, value)
            value = int(round(value))
            rv = u'%s %s' % (value, unit)
            if value != 1:
                rv += u's'
            return rv
    return u''


def parse_db_url(name):
    """Parses the given db URL string and returns it's components

    The string form of the URL is
    `dialect[+driver]://user:password@host/dbname[?key=value]`, where
    `dialect` is a database name such as `mysql`, `oracle`,
    `driver` the name of a DPAPI, such as psycop2
    """

    # def _parse_rfc1738_args(name):
    pattern = re.compile(r'''
            (?P<name>[\w\+]+)://
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>.*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )?
                (?::(?P<port>[^/]*))?
            )?
            (?:/(?P<database>.*))?
            ''', re.X)

    m = pattern.match(name)
    if m is not None:
        components = m.groupdict()
        if components['database'] is not None:
            tokens = components['database'].split('?', 2)
            components['database'] = tokens[0]
            query = (
                len(tokens) > 1 and dict(parse_qsl(tokens[1]))) or None
        else:
            query = None
        components['query'] = query

        if components['username'] is not None:
           components['username'] = _rfc_1738_unquote(components['username'])

        if components['password'] is not None:
           components['password'] = _rfc_1738_unquote(components['password'])

        ipv4host = components.pop('ipv4host')
        ipv6host = components.pop('ipv6host')
        components['host'] = ipv4host or ipv6host
        name = components.pop('name')

        dialect_driver = name.split('+', 1)
        dialect = dialect_driver[0]
        driver = None if len(dialect_driver) == 1 else dialect_driver[1]
        components['dialect'] = dialect
        components['driver'] = driver
        return components
        # return URL(name, **components)
    else:
        raise ValueError("Could not parse rfc1738 URL from string '%s'" % name)


def _rfc_1738_quote(text):
    return re.sub(r'[:@/]', lambda m: "%%%X" % ord(m.group(0)), text)


def _rfc_1738_unquote(text):
    return unquote(text)


_PROTECTED_TYPES = integer_types + (
    type(None), float, Decimal, datetime.datetime, datetime.date, datetime.time
)


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.
    Objects of protected types are preserved as-is when passed to
    force_text(strings_only=True).
    """
    return isinstance(obj, _PROTECTED_TYPES)


def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.
    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if issubclass(type(s), text_type):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not issubclass(type(s), string_types):
            if PY3:
                if isinstance(s, bytes):
                    s = text_type(s, encoding, errors)
                else:
                    s = text_type(s)
            elif hasattr(s, '__unicode__'):
                s = text_type(s)
            else:
                s = text_type(bytes(s), encoding, errors)
        else:
            # Note: We use .decode() here, instead of text_type(s, encoding,
            # errors), so that if s is a SafeBytes, it ends up being a
            # SafeText at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise UnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = ' '.join(force_unicode(arg, encoding, strings_only, errors)
                         for arg in s)
    return s
