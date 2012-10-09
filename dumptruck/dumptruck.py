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
from convert import convert, quote, simplify
from adapters_and_converters import register_adapters_and_converters, Pickle, replace_date_converter

PYTHON_SQLITE_TYPE_MAP={
  unicode: u'text',
  str: u'text',

  int: u'integer',
  long: u'integer',
  bool: u'boolean',
  float: u'real',

  datetime.date: u'date',
  datetime.datetime: u'datetime',

  dict: u'json text',
  list: u'json text',
  set: u'jsonset text',
}

def get_column_type(obj):
  'Decide the type of a column to contain an object.'
  return u'pickle text' if isinstance(obj, Pickle) else PYTHON_SQLITE_TYPE_MAP[type(obj)]

# Only for compatibility with scraperwiki;
# we should use the SQLite names
#SWVARIABLES_PYTHON_TYPE_MAP={
#  u'float': float
#}

class DumpTruck:
  'A relaxing interface to SQLite'


  def __init__(self, dbname = 'dumptruck.db', vars_table = '_dumptruckvars', vars_table_tmp = '_dumptruckvarstmp', auto_commit = True, adapt_and_convert = True):

    self.sqlite3 = __import__('sqlite3')

    if adapt_and_convert:
        register_adapters_and_converters(self.sqlite3)
    else:
        replace_date_converter(self.sqlite3)

    # Should database changes be committed automatically after each command?
    if type(auto_commit) != bool:
      raise TypeError('auto_commit must be True or False.')
    else:
      self.auto_commit = auto_commit

    # Database connection
    if type(dbname) not in [unicode, str]:
      raise TypeError('dbname must be a string')
    else:
      self.connection=self.sqlite3.connect(dbname, detect_types = self.sqlite3.PARSE_DECLTYPES)
      self.cursor=self.connection.cursor()

    # Make sure it's a good table name
    if type(vars_table) not in [unicode, str]:
      raise TypeError('vars_table must be a string')
    else:
      self.__vars_table = vars_table

    # Make sure it's a good table name
    if type(vars_table_tmp) not in [unicode, str]:
      raise TypeError('vars_table_tmp must be a string')
    else:
      self.__vars_table_tmp = vars_table_tmp

  def __check_or_create_vars_table(self):
    sql = u"CREATE TABLE IF NOT EXISTS %s (`key` text PRIMARY KEY, `value` blob, `type` text)" % quote(self.__vars_table)
    self.execute(sql, commit = False)

    self.commit()

    table_info = self.execute(u'PRAGMA table_info(%s)' % quote(self.__vars_table))
    column_names_observed = set([column['name'] for column in table_info])
    column_names_expected = {'key', 'type', 'value'}
    assert column_names_observed == column_names_expected, table_info

  def execute(self, sql, *args, **kwargs):
    '''
    Run raw SQL on the database, and receive relaxing output.
    This is sort of the foundational method that most of the
    others build on.
    '''
    try:
      self.cursor.execute(sql, *args)
    except self.sqlite3.InterfaceError, msg:
      raise self.sqlite3.InterfaceError(unicode(msg) + '\nTry converting types or pickling.')
    rows = self.cursor.fetchall()

    self.__commit_if_necessary(kwargs)

    if None == self.cursor.description:
      return None
    else:
      colnames = [d[0].decode('utf-8') for d in self.cursor.description] 
      rawdata = [OrderedDict(zip(colnames,row)) for row in rows]
      return rawdata

  def commit(self):
    'Commit database transactions.'
    return self.connection.commit()

  def close(self):
    return self.connection.close()

  def create_index(self, columns, table_name, if_not_exists = True, unique = False, **kwargs):
    'Create a unique index on the column(s) passed.'
    index_name = simplify(table_name) + u'_' + u'_'.join(map(simplify, columns))
    if unique:
      sql = u'CREATE UNIQUE INDEX %s ON %s (%s)'
    else:
      sql = u'CREATE INDEX %s ON %s (%s)'

    first_param = u'IF NOT EXISTS ' + index_name if if_not_exists else index_name

    params = (first_param, quote(table_name), ','.join(map(quote, columns)))
    self.execute(sql % params, **kwargs)

  def __column_types(self, table_name):
    # This is vulnerable to injection.
    self.cursor.execute(u'PRAGMA table_info(%s)' % quote(table_name))
    return {column[1]:column[2] for column in self.cursor.fetchall()}

  def __check_and_add_columns(self, table_name, converted_data_row):
    column_types = self.__column_types(table_name)
    for key,value in converted_data_row:
      try:
        column_type = get_column_type(value)
        params = (quote(table_name), key, column_type)
        sql = u'ALTER TABLE %s ADD COLUMN %s %s ' % params
        self.execute(sql, commit = True)
      except self.sqlite3.OperationalError, msg:
        if str(msg).split(':')[0] == u'duplicate column name':
          # The column is already there.
          pass
        else:
          raise

  def __cast_data_to_column_type(self, data):
    column_types = self.__column_types(table_name)
    for key,value in data.items():
      if SQLITE_TYPE_MAP[type(key)] != column_types[key]:
        try:
          data[key] = type(key)(value)
        except ValueError:
          raise TypeError(u'Data could not be converted to match the existing `%s` column type.')

  def create_table(self, data, table_name, error_if_exists = False, **kwargs):
    'Create a table based on the data, but don\'t insert anything.'

    converted_data = convert(data)
    if len(converted_data) == 0 or converted_data[0] == []:
      raise ValueError(u'You passed no sample values, or all the values you passed were null.')
    else:
      startdata = OrderedDict(converted_data[0])

    # Select a non-null item
    for k, v in startdata.items():
      if v != None:
        break
    else:
      v = None

    if_not_exists = u'' if error_if_exists else u'IF NOT EXISTS'

    # Do nothing if all items are null.
    if v != None:
      try:
        # This is vulnerable to injection.
        sql = u'''
          CREATE TABLE %s %s (
            %s %s
          );''' % (if_not_exists, quote(table_name), quote(k), get_column_type(startdata[k]))
        self.execute(sql, commit = False)
      except:
        raise
      else:
        self.commit()
 
      for row in converted_data:
        self.__check_and_add_columns(table_name, row)


  def insert(self, data, table_name = 'dumptruck', **kwargs):
    # Skip if empty
    if len(data) == 0 and not hasattr(data, 'keys'):
      return []

    try:
      self.create_table(data, table_name, error_if_exists = True)
    except ValueError, msg_raw:
      msg = unicode(msg_raw)
      msgs = {
        u'Data must contain at least one row.',
        u'First data row must contain at least one column.',
        u'You passed no sample values, or all the values you passed were null.'
      }

      if table_name in self.tables() and msg in msgs:
        pass
      else:
        raise
    except self.sqlite3.OperationalError, msg_raw:
      if u'already exists' in unicode(msg_raw):
        pass
    except:
      raise

    # Turn it into a list of zips.
    converted_data = convert(data)

    for row in converted_data:
      self.__check_and_add_columns(table_name, row)
    
    # .keys() and .items() are in the same order
    # http://www.python.org/dev/peps/pep-3106/

    # rowid of inserted rows
    rowids = []
    for row in converted_data:
      keys = [pair[0] for pair in row]
      values = [pair[1] for pair in row]

      # This is vulnerable to injection.
      if len(keys) > 0:
        question_marks = ','.join('?'*len(keys))
        sql = u'INSERT INTO %s (%s) VALUES (%s);' % (quote(table_name), ','.join(keys), question_marks)
        self.execute(sql, values, commit=False)

      else:
        sql = u'INSERT INTO %s DEFAULT VALUES;' % quote(table_name) 
        self.execute(sql, commit=False)

      rowids.append(self.execute('SELECT last_insert_rowid()', commit=False)[0]['last_insert_rowid()'])

    self.__commit_if_necessary(kwargs)

    # Return rowids as a list?
    if hasattr(data, 'keys'):
      return rowids[0]
    else:
      return rowids

  def __commit_if_necessary(self, kwargs):
    if kwargs.get('commit', self.auto_commit):
      self.commit()

  def get_var(self, key):
    'Retrieve one saved variable from the database.'
    vt = quote(self.__vars_table)
    data = self.execute(u'SELECT * FROM %s WHERE `key` = ?' % vt, [key], commit = False)
    if data == []:
      raise NameError(u'The DumpTruck variables table doesn\'t have a value for %s.' % key)
    else:
      tmp = quote(self.__vars_table_tmp)
      row = data[0]

      self.execute(u'DROP TABLE IF EXISTS %s' % tmp, commit = False)

      # This is vulnerable to injection
      self.execute(u'CREATE TEMPORARY TABLE %s (`value` %s)' % (tmp, row['type']), commit = False)

      # This is ugly
      self.execute(u'INSERT INTO %s (`value`) VALUES (?)' % tmp, [row['value']], commit = False)
      value = self.dump(tmp)[0]['value']
      self.execute(u'DROP TABLE %s' % tmp, commit = False)

      return value

  def save_var(self, key, value, **kwargs):
    'Save one variable to the database.'

    # Check whether Highwall's variables table exists
    self.__check_or_create_vars_table()

    column_type = get_column_type(value)
    tmp = quote(self.__vars_table_tmp)

    self.execute(u'DROP TABLE IF EXISTS %s' % tmp, commit = False)

    # This is vulnerable to injection
    self.execute(u'CREATE TABLE %s (`value` %s)' % (tmp, column_type), commit = False)

    # This is ugly
    self.execute(u'INSERT INTO %s (`value`) VALUES (?)' % tmp, [value], commit = False)
    table = (quote(self.__vars_table), tmp)
    params = [key, column_type]
    self.execute(u'''
INSERT OR REPLACE INTO %s (`key`, `type`, `value`)
  SELECT
    ? AS key,
    ? AS type,
    value
  FROM %s
''' % table, params)
    self.execute(u'DROP TABLE %s' % tmp, commit = False)

    self.__commit_if_necessary(kwargs)

  def tables(self):
    result = self.execute(u'SELECT name FROM sqlite_master WHERE TYPE="table"', commit = False)
    return set([row['name'] for row in result])

  def drop(self, table_name = 'dumptruck', if_exists = False, **kwargs):
    'Drop a table.'
    return self.execute(u'DROP TABLE %s %s;' % ('IF EXISTS' if if_exists else '', quote(table_name)), **kwargs)

  def dump(self, table_name = 'dumptruck'):
    'Dump a table.'
    return self.execute(u'SELECT * FROM %s;' % quote(table_name))

