#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
"""Relaxing interface to SQLite"""

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
from sqlalchemy.dialects.sqlite import TEXT, INTEGER, BOOLEAN, FLOAT, DATE, DATETIME, BLOB
from convert import convert, simplify

import old_dumptruck

class JSONObject(sqlalchemy.TypeDecorator):
    """Represents a dict, list or set as a json-encoded string."""

    impl = TEXT

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

class Blob(str):
    """Represents a string as a blob."""

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
    set: JSONObject,

    Blob: BLOB
}

class DumpTruck(old_dumptruck.DumpTruck):
    def __init__(self, dbname = 'dumptruck.db', vars_table = '_dumptruckvars', auto_commit=True, adapt_and_convert=True, timeout=5):
        self.auto_commit = auto_commit

        self.engine = sqlalchemy.create_engine('sqlite:///{}'.format(dbname), echo=True, connect_args={'timeout': timeout})
        self.conn = self.engine.connect()
        self.trans = self.conn.begin()

        self.__vars_table = vars_table

    def execute(self, sql_query, *args, **kwargs):
        """
        Execute an arbitrary SQL query given by sql_query, returning any
        results as a list of OrderedDicts. A list of data can be supplied,
        which is substitued into question marks in the query.
        """
        data = args

        if kwargs.get('commit', self.auto_commit):
            self.trans.commit()
            with self.conn.begin() as transaction:
                result = self.conn.execute(sql_query, data)
            self.trans = self.conn.begin()
        else:
            result = self.conn.execute(sql_query, data)

        if not result.returns_rows:
            return None

        return [OrderedDict(row) for row in result.fetchall()]

    def upsert(self, *args, **kwargs):
        """
        Insert the given data into the table table_name, where data is a list
        of dictionaries keyed by column name. Inserting a row with an index value
        already present in the database will result in the row being replaced.
        """
        self.insert(upsert=True, *args, **kwargs)

    def insert(self, data, table_name='dumptruck', upsert=False, **kwargs):
        """
        Insert the given data into the table table_name, where data is a list
        of dictionaries keyed by column name. If upsert is True, inserting a row
        with an index value already present in the database will result in the row
        being replaced, otherwise doing so will generate an error.
        """
        # Skip if empty
        if len(data) == 0 and not hasattr(data, 'keys'):
            return

        prefixes = ['OR REPLACE'] if upsert else []

        for row in data:
            metadata = sqlalchemy.MetaData(bind=self.engine)
            metadata.reflect(only=[table_name])

            table = sqlalchemy.Table(table_name, metadata, extend_existing=True)

            ins = table.insert(prefixes=prefixes).values(data)
            self.conn.execute(ins)

        if kwargs.get('commit', self.auto_commit):
            self.commit()

    def create_table(self, data, table_name, **kwargs):
        """
        Create a new table with name table_name and column names and types
        based on the first element of data, where data is a list of dictionaries or
        OrderedDicts keyed by column name. If the table already exists, it will be
        altered to include any new columns.
        """
        converted_data = convert(data)

        if len(converted_data) == 0 or converted_data[0] == []:
            raise ValueError('You passed no sample values, or all the values you passed were None.')
        else:
            startdata = OrderedDict(converted_data[0])

        metadata = sqlalchemy.MetaData(bind=self.engine)
        metadata.reflect()

        table = sqlalchemy.Table(table_name, metadata, extend_existing=True)
        original_columns = list(table.columns)

        new_columns = []
        for column_name, column_value in startdata.items():
            new_column = sqlalchemy.Column(column_name, self.get_column_type(column_value))
            if not str(new_column) in table.columns:
                new_columns.append(new_column)
                table.append_column(new_column)

        with self.conn.begin() as transaction:
            metadata.create_all(self.engine)

            if original_columns != list(table.columns) and original_columns != []:
                for new_column in new_columns:
                    s = sqlalchemy.sql.text('ALTER TABLE {} ADD {} {}'.format(table_name, new_column.name, new_column.type))
                    self.conn.execute(s)

    def drop_table(self, table_name='dumptruck', if_exists=False, **kwargs):
        """
        Drop a table. If if_exists is True, the existence of the table
        will be checked first, otherwise dropping a nonexistant table
        will result in an error.
        """
        metadata = sqlalchemy.MetaData(bind=self.engine)
        metadata.reflect()

        table = sqlalchemy.Table(table_name, metadata)

        table.drop(bind=self.engine, checkfirst=if_exists)

    def create_index(self, column_names, table_name, if_not_exists=True, unique=False, **kwargs):
        """
        Create a new index of the columns in column_names, where column_names is a list of strings,
        on table table_name. If unique is True, it will be a unique index. If if_not_exists is True,
        the index be checked to make sure it does not already exists, otherwise creating duplicate
        indices will result in an error.
        """
        metadata = sqlalchemy.MetaData(bind=self.engine)
        metadata.reflect()
        table = sqlalchemy.Table(table_name, metadata)

        index_name = simplify(table_name) + '_' + '_'.join(map(simplify, column_names))

        columns = []
        for column_name in column_names:
            columns.append(table.columns[column_name])

        current_indices = [x.name for x in table.indexes]
        index = sqlalchemy.schema.Index(index_name, *columns, unique=unique)
        if index.name not in current_indices or not if_not_exists:
            index.create(bind=self.engine)

    def save_var(self, key, value, **kwargs):
        """Save one variable to the database."""
        column_type = self.get_column_type(value)
        row = OrderedDict([['key', key], ['value', Blob(value)], ['type', str(column_type)]])

        self.create_table([row], self.__vars_table)
        self.insert([row], self.__vars_table)

    def get_column_type(self, column_value):
        """Return the appropriate SQL column type for the given value."""
        return PYTHON_SQLITE_TYPE_MAP[type(column_value)]

    def commit(self):
        """Commit any pending changes to the database."""
        self.trans.commit()
        self.trans = self.conn.begin()
