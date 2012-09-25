#!/usr/bin/env python2
'SQLite adapter and converter functions'

# Copyright 2012 Thomas Levine

# This file is part of DumpTruck.

# DumpTruck is free software: you can redistribute it and/or modify
# it under the terms of the GNU Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# DumpTruck is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Public License for more details.

# You should have received a copy of the GNU Public License
# along with DumpTruck.  If not, see <http://www.gnu.org/licenses/>.

import pickle
import json
import datetime

class Pickle:
    def __init__(self, obj):
        self.obj = obj

def register_big(module):
    def adapt_long(val):
        'Handle very large integers.'
        return float(val)

    module.register_adapter(long, adapt_long)

def register_unicode(module):
    def text(val):
        return val.decode('utf-8')

    module.register_adapter(unicode, text)
    module.register_adapter(str, text)
    module.register_converter('TEXT', text)
    module.register_converter('text', text)

def register_pickle(module):
    def adapt_pickle(val):
        return pickle.dumps(val.obj)

    def convert_pickle(val):
        return pickle.loads(val)

    module.register_adapter(Pickle, adapt_pickle)
    module.register_converter('PICKLE', convert_pickle)
    module.register_converter('pickle', convert_pickle)

def register_json(module):
    def adapt_json(val):
        return json.dumps(val, ensure_ascii=True)

    def adapt_jsonset(val):
        d = {k: None for k in val}
        return json.dumps(d, ensure_ascii=True)

    def convert_json(val):
        return json.loads(val)

    def convert_jsonset(val):
        return set(json.loads(val).keys())

    module.register_adapter(list, adapt_json)
    module.register_adapter(tuple, adapt_json)
    module.register_adapter(dict, adapt_json)
    module.register_adapter(set, adapt_jsonset)
    module.register_converter('json', convert_json)
    module.register_converter('JSON', convert_json)
    module.register_converter('jsonset', convert_jsonset)
    module.register_converter('JSONSET', convert_jsonset)

def register_dates(module):
    def adapt_date(val):
        return val.isoformat()

    def adapt_datetime(val):
        return val.isoformat(' ')

    def convert_date(val):
        return datetime.date(*map(int, val.split('-')))

    def convert_datetime(val):
        datepart, timepart = val.split(' ')
        year, month, day = map(int, datepart.split('-'))
        timepart_full = timepart.split('.')
        hours, minutes, seconds = map(int, timepart_full[0].split(':'))
        if len(timepart_full) == 2:
            microseconds = int(timepart_full[1])
        else:
            microseconds = 0

        val = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds)
        return val

    module.register_adapter(datetime.date, adapt_date)
    module.register_adapter(datetime.datetime, adapt_datetime)
    module.register_converter('DATE', convert_date)
    module.register_converter('date', convert_date)
    module.register_converter('DATETIME', convert_datetime)
    module.register_converter('datetime', convert_datetime)

def register_adapters_and_converters(module):
#   register_big(module)
    register_dates(module)
    register_json(module)
    register_pickle(module)
    register_unicode(module)
