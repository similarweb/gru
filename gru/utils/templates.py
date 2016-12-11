import dateutil.parser
from dateutil import tz
from collections import Mapping, Sequence
import datetime
import json


def flatten(o, prefix=''):
    if isinstance(o, dict):
        d1 = {}
        for k, v in o.iteritems():
            new_prefix = prefix + '.' + k if prefix else k
            v1 = flatten(v, new_prefix)
            d1.update(v1)
        return d1
    else:
        return {prefix: o}


def prettytime(datestr):
    dt = dateutil.parser.parse(datestr)
    utc_dt = dt.astimezone(tz.gettz('UTC'))
    return utc_dt.strftime('%d/%m/%Y %H:%M:%S')


def pretty_unix_ts(ts):
    return datetime.datetime.fromtimestamp(
        int(ts)
    ).strftime('%d/%m/%Y %H:%M:%S')


def to_json_pretty(s):
    return json.dumps(s, indent=2)


def prettify_structured(obj):
    if isinstance(obj, basestring):
        return obj
    elif isinstance(obj, Mapping):
        return to_json_pretty(obj)
    elif isinstance(obj, Sequence):
        return ", ".join(str(obj))
    else:
        return str(obj)


def setup(app):
    app.template_filter('flatten')(flatten)
    app.template_filter('prettytime')(prettytime)
    app.template_filter('to_json_pretty')(to_json_pretty)
    app.template_filter('prettify_structured')(prettify_structured)
    app.template_filter('pretty_unix_ts')(pretty_unix_ts)