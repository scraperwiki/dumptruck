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
from collections import OrderedDict
import sqlalchemy
from sqlalchemy.dialects.sqlite import TEXT, INTEGER, BOOLEAN, REAL, DATE, DATETIME, BLOB

class NoMicrosecondDatetime(DATETIME):
    """
    Allows us to store datetime objects without added microseconds.
    """
    def __init__(self, *args, **kwargs):
        super(NoMicrosecondDatetime, self).__init__(truncate_microseconds=True, *args, **kwargs)

    def adapt(self, impltype, *args, **kwargs):
        return NoMicrosecondDatetime(*args, **kwargs)

class Blob(str):
    """Represents a blob as a string."""
    def __init__(self, *args, **kwargs):
        super(Blob, self).__init__(*args, **kwargs)

PYTHON_SQLITE_TYPE_MAP = {
    unicode: TEXT,
    str: TEXT,

    int: INTEGER,
    long: INTEGER,
    bool: BOOLEAN,
    float: REAL,

    datetime.date: DATE,
    datetime.datetime: DATETIME,

    Blob: BLOB
}

class DumpTruck:
    def __init__(self, dbname = 'dumptruck.db', vars_table = '_dumptruckvars', auto_commit=True, timeout=5, **kwargs):
        if type(auto_commit) is bool:
            self.auto_commit = auto_commit
        else:
            raise TypeError('auto_commit must be a boolean value')

        if type(vars_table) in (str, unicode, None):
            self.__vars_table = vars_table
        else:
            raise TypeError('vars_table must be a string or unicode string')

        if not type(dbname) in (str, unicode, None):
            raise TypeError('dbname must be a string or unicode string')

        self.engine = sqlalchemy.create_engine('sqlite:///{}'.format(dbname), echo=False, connect_args={'timeout': timeout})
        self.conn = self.engine.connect()
        self.trans = self.conn.begin()
        self.connection = self.trans # To preserve API

    def execute(self, sql_query, *args, **kwargs):
        """
        Execute an arbitrary SQL query given by sql_query, returning any
        results as a list of OrderedDicts. A list of values can be supplied as an,
        additional argument, which will be substitued into question marks in the query.
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
        if len(data) == 0:
            return

        if type(data) in (dict, OrderedDict):
            data = [data]

        prefixes = ['OR REPLACE'] if upsert else []

        metadata = sqlalchemy.MetaData(bind=self.engine)

        try:
            metadata.reflect(only=[table_name])
        except sqlalchemy.exc.InvalidRequestError:
            raise ValueError("no such table: {}".format(table_name))

        table = sqlalchemy.Table(table_name, metadata, extend_existing=True)

        for col in table.c:
            if col.type.__visit_name__  == 'DATETIME':
                col.type = NoMicrosecondDatetime

        for row in data:
            ins = table.insert(prefixes=prefixes).values(data)
            self.conn.execute(ins)

        if kwargs.get('commit', self.auto_commit):
            self.commit()

    def create_table(self, data, table_name, error_if_exists=False, **kwargs):
        """
        Create a new table with name table_name and column names and types
        based on the first element of data. Data can be a single data element,
        or a list of data elements where a data element is a dictionaries or
        OrderedDicts keyed by column name. If the table already exists, it
        will be altered to include any new columns.
        """
        if type(data) == OrderedDict or type(data) == dict:
            startdata = data
        else:
            if len(data) > 0:
                startdata = data[0]
            else:
                startdata = {}

        all_none = True
        for value in startdata.values():
            if value is not None:
                all_none = False
                break

        if len(data) == 0 or all_none:
            raise ValueError('You passed no sample values, or all the values you passed were None.')

        metadata = sqlalchemy.MetaData(bind=self.engine)
        metadata.reflect()

        if error_if_exists and table_name in metadata.tables.keys():
            raise sqlalchemy.exc.OperationalError('table already exists: {}'.format(table_name))

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

        index_name = re.sub(r'[^a-zA-Z0-9]', '', table_name) + '_'
        index_name += '_'.join(map(lambda x: re.sub(r'[^a-zA-Z0-9]', '', x), column_names))

        columns = []
        for column_name in column_names:
            columns.append(table.columns[column_name])

        current_indices = [x.name for x in table.indexes]
        index = sqlalchemy.schema.Index(index_name, *columns, unique=unique)
        if index.name not in current_indices or not if_not_exists:
            index.create(bind=self.engine)

    def save_var(self, key, value, **kwargs):
        """
        Save a variable to the table specified by self.vars_table. Key is
        the name of the variable, and value is the value.
        """
        column_type = self.get_column_type(value)
        type_row = OrderedDict([['key', ''], ['value', Blob()], ['type', '']])
        data_row = OrderedDict([['key', key], ['value', Blob(value)], ['type', column_type.__visit_name__.lower()]])

        self.create_table([type_row], self.__vars_table)
        self.create_index(['key'], self.__vars_table, unique=True)
        self.upsert([data_row], self.__vars_table)

        if kwargs.get('commit', self.auto_commit):
            self.commit()

    def get_var(self, key):
        """
        Returns the variable with the provided key from the
        table specified by self.vars_table.
        """
        self.commit()

        metadata = sqlalchemy.MetaData(bind=self.engine)
        metadata.reflect()
        table = sqlalchemy.Table(self.__vars_table, metadata)

        s = sqlalchemy.select([table.c.value, table.c.type]).where(table.c.key == key)
        result = self.conn.execute(s).fetchone()

        # Insert data into temporary table and select it, to get the right type
        self.execute("CREATE TEMPORARY TABLE tmp ('value' {0})".format(result.type))
        t = sqlalchemy.sql.text("INSERT INTO tmp VALUES (:value)")
        self.conn.execute(t, value=result.value)
        var = self.dump('tmp')[0].get('value')
        self.execute("DROP TABLE tmp")

        if not result:
            raise NameError('The DumpTruck variables table doesn\'t have a value for %s.' % key)
        else:
            return var

    def get_column_type(self, column_value):
        """
        Return the appropriate SQL column type for the given value.
        """
        if type(column_value) == datetime.datetime and column_value.microsecond == 0:
            return NoMicrosecondDatetime

        return PYTHON_SQLITE_TYPE_MAP[type(column_value)]

    def tables(self):
        """
        Return a set of the names of the tables currently in the database.
        """
        metadata = sqlalchemy.MetaData(bind=self.engine)
        metadata.reflect()
        return set(metadata.tables.keys())

    def commit(self):
        """
        Commit any pending changes to the database.
        """
        self.trans.commit()
        self.trans = self.conn.begin()

    def close(self):
        """
        Close the connection to the database.
        """
        self.conn.close()

    def dump(self, table_name='dumptruck'):
        """
        Return the complete contents of the table table_name.
        """
        return self.execute("SELECT * FROM {}".format(table_name))
