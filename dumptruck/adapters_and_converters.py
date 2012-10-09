#!/usr/bin/env python2
'SQLite adapter and converter functions'

# This file is part of DumpTruck.

# Copyright (C) 2012 ScraperWiki Ltd. and other contributors
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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

def replace_date_converter(module):
    module.register_converter('DATE', lambda val: val)
    module.register_converter('DATETIME', lambda val: val)
    module.register_converter('TIME' + 'STAMP', lambda val: val)
