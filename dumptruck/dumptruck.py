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
from collections import OrderedDict
import sqlalchemy
from convert import convert, quote, simplify
from adapters_and_converters import register_adapters_and_converters, Pickle, replace_date_converter

import old_dumptruck

class DumpTruck(old_dumptruck.DumpTruck):
    def __init__(self, dbname = 'dumptruck.db', vars_table = '_dumptruckvars', vars_table_tmp = '_dumptruckvarstmp', auto_commit = True, adapt_and_convert = True, timeout = 5):
        self.auto_commit = auto_commit

        engine = sqlalchemy.create_engine('sqlite:///{}'.format(dbname), echo=True, connect_args={'timeout': timeout})
        self.conn = engine.connect()
        self.trans = self.conn.begin()

    def execute(self, sql_query, *args, **kwargs):
        s = sqlalchemy.sql.text(sql_query)
        result = self.conn.execute(s)

        self.__commit_if_necessary(kwargs)

        if not result.returns_rows:
            return None

        return [OrderedDict(row) for row in result.fetchall()]


    def commit(self):
        'Commit database transactions and start a new transaction.'
        self.trans.commit()
        self.trans = self.conn.begin()
