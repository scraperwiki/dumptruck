#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
'Relaxing interface to SQLite'

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

import re
import datetime
import json
from collections import OrderedDict
import sqlalchemy
from sqlalchemy.dialects.sqlite import TEXT, INTEGER, BOOLEAN, FLOAT, DATE, DATETIME 
from convert import convert

import old_dumptruck

class JSONObject(sqlalchemy.TypeDecorator):
    """Represents a dict, list or set as a json-encoded string."""

    impl = sqlalchemy.String

    def process_bind_param(self, value, dialect):
        if value is not None:
            if type(value) == dict or type(value) == list or type(value) == set:
                if type(value) == set:
                    value = list(value)
                value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

PYTHON_SQLITE_TYPE_MAP = {
    unicode: TEXT,
    str: TEXT,

    int: INTEGER,
    long: INTEGER,
    bool: BOOLEAN,
    float: FLOAT,

    datetime.date: DATE,
    datetime.datetime: DATETIME,

    dict: JSONObject,
    list: JSONObject,
    set: JSONObject
}

class DumpTruck(old_dumptruck.DumpTruck):
    def __init__(self, dbname = 'dumptruck.db', vars_table = '_dumptruckvars', vars_table_tmp = '_dumptruckvarstmp', auto_commit = True, adapt_and_convert = True, timeout = 5):
        self.auto_commit = auto_commit

        self.engine = sqlalchemy.create_engine('sqlite:///{}'.format(dbname), echo=True, connect_args={'timeout': timeout})
        self.conn = self.engine.connect()
        self.trans = self.conn.begin()

    def execute(self, sql_query, *args, **kwargs):
        s = sqlalchemy.sql.text(sql_query)

        if kwargs.get('commit', self.auto_commit):
            with self.conn.begin() as transaction:
                result = self.conn.execute(s)
        else:
            result = self.conn.execute(s)

        if not result.returns_rows:
            return None

        return [OrderedDict(row) for row in result.fetchall()]

    def insert(self, data, table_name='dumptruck', upsert=False, **kwargs):
        pass

    def create_table(self, data, table_name, **kwargs):
        converted_data = convert(data)

        if len(converted_data) == 0 or converted_data[0] == []:
            raise ValueError('You passed no sample values, or all the values you passed were null.')
        else:
            startdata = OrderedDict(converted_data[0])

        metadata = sqlalchemy.MetaData()
        table = sqlalchemy.Table(table_name, metadata)

        for column_name, column_value in startdata.items():
            table.append_column(sqlalchemy.Column(column_name, self.get_column_type(column_value)))

        with self.conn.begin() as transaction:
            metadata.create_all(self.engine)

    def get_column_type(self, column_value):
        return PYTHON_SQLITE_TYPE_MAP[type(column_value)]

    def commit(self):
        self.trans.commit()
        self.trans = self.conn.begin()
