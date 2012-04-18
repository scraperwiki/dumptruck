#!/usr/bin/env python2
"Relaxing interface to SQLite"

# Copyright 2012 Thomas Levine

# This file is part of DumpTruck.

# DumpTruck is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# DumpTruck is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.

# You should have received a copy of the GNU Affero Public License
# along with DumpTruck.  If not, see <http://www.gnu.org/licenses/>.

import json
import sqlite3
import re
import datetime
from convert import convert, quote, simplify
from adapters_and_converters import register_adapters_and_converters, Pickle

register_adapters_and_converters(sqlite3)
del(register_adapters_and_converters)

PYTHON_SQLITE_TYPE_MAP={
  unicode: u"text",
  str: u"text",

  int: u"integer",
  long: u"integer",
  bool: u"boolean",
  float: u"real",

  datetime.date: u"date",
  datetime.datetime: u"datetime",

  dict: u"json text",
  list: u"json text",
  set: u"jsonset text",
}

def get_column_type(obj):
  "Decide the type of a column to contain an object."
  return "pickle text" if isinstance(obj, Pickle) else PYTHON_SQLITE_TYPE_MAP[type(obj)]

# Only for compatibility with scraperwiki;
# we should use the SQLite names
#SWVARIABLES_PYTHON_TYPE_MAP={
#  u"float": float
#}

class DumpTruck:
  "A relaxing interface to SQLite"

  def __init__(self, dbname = "dumptruck.db", vars_table = "_dumptruckvars", vars_table_tmp = "_dumptruckvarstmp", auto_commit = True):
    pass
    # Should database changes be committed automatically after each command?
    if type(auto_commit) != bool:
      raise TypeError("auto_commit must be True or False.")
    else:
      self.auto_commit = auto_commit

    # Database connection
    if type(dbname) not in [unicode, str]:
      raise TypeError("dbname must be a string")
    else:
      self.connection=sqlite3.connect(dbname, detect_types = sqlite3.PARSE_DECLTYPES)
      self.cursor=self.connection.cursor()

    # Make sure it's a good table name
    if type(vars_table) not in [unicode, str]:
      raise TypeError("vars_table must be a string")
    else:
      self.__vars_table = vars_table

    # Make sure it's a good table name
    if type(vars_table_tmp) not in [unicode, str]:
      raise TypeError("vars_table_tmp must be a string")
    else:
      self.__vars_table_tmp = vars_table_tmp

  def __check_or_create_vars_table(self):
    self.create_table(
      {'key': '', 'type': ''},
      quote(self.__vars_table),
      commit = False
    )
    sql = 'ALTER TABLE %s ADD COLUMN value BLOB' % quote(self.__vars_table)
    self.execute(sql, commit = False)

    self.commit()

    table_info = self.execute('PRAGMA table_info(%s)' % quote(self.__vars_table))
    column_names_observed = set([column['name'] for column in table_info])
    column_names_expected = set(['key', 'type', 'value'])
    assert column_names_observed == column_names_expected, table_info

  def execute(self, sql, *args, **kwargs):
    """
    Run raw SQL on the database, and receive relaxing output.
    This is sort of the foundational method that most of the
    others build on.
    """
    self.cursor.execute(sql, *args)
    rows = self.cursor.fetchall()

    self.__commit_if_necessary(kwargs)

    if None == self.cursor.description:
      return None
    else:
      colnames = [d[0] for d in self.cursor.description] 
      rawdata = [dict(zip(colnames,row)) for row in rows]
      return rawdata

  def commit(self):
    "Commit database transactions."
    return self.connection.commit()

  def close(self):
    return self.connection.close()

  def create_index(self, table_name, columns, if_not_exists = True, unique = False, **kwargs):
    "Create a unique index on the column(s) passed."
    index_name = 'dumptruck_' + simplify(table_name) + '__' + '_'.join(map(simplify, columns))
    if unique:
      sql = "CREATE UNIQUE INDEX %s ON %s (%s)"
    else:
      sql = "CREATE INDEX %s ON %s (%s)"

    first_param = 'IF NOT EXISTS ' + index_name if if_not_exists else index_name

    params = (first_param, quote(table_name), ','.join(map(quote, columns)))
    self.execute(sql % params, **kwargs)

  def __column_types(self, table_name):
    # This is vulnerable to injection.
    self.cursor.execute("PRAGMA table_info(%s)" % quote(table_name))
    return {column[1]:column[2] for column in self.cursor.fetchall()}

  def __check_and_add_columns(self, table_name, converted_data_row):
    column_types = self.__column_types(table_name)
    for key,value in converted_data_row.items():
      try:
        column_type = get_column_type(value)
        params = (quote(table_name), key, column_type)
        sql = 'ALTER TABLE %s ADD COLUMN %s %s ' % params
        self.execute(sql, commit = True)
      except sqlite3.OperationalError, msg:
        if str(msg).split(':')[0] == 'duplicate column name':
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
          raise TypeError("Data could not be converted to match the existing `%s` column type.")

  def create_table(self, data, table_name, error_if_exists = False, **kwargs):
    "Create a table based on the data, but don't insert anything."
    converted_data = convert(data)
    startdata = converted_data[0]

    # Select a non-null item
    for k, v in startdata.items():
      if v != None:
        break

    try:
      # This is vulnerable to injection.
      self.execute("""
        CREATE TABLE %s (
          %s %s
        );""" % (quote(table_name), quote(k), get_column_type(startdata[k])), commit = False)
    except sqlite3.OperationalError, msg:
      if (not re.match(r'^table.+already exists$', str(msg))) or (error_if_exists == True):
        raise
    else:
      self.commit()

    for row in converted_data:
      self.__check_and_add_columns(table_name, row)


  def insert(self, data, table_name = "dumptruck", **kwargs):
    try:
      self.create_table(data, table_name)
    except:
      raise

    converted_data = convert(data)

    for row in converted_data:
      self.__check_and_add_columns(table_name, row)
    
    # .keys() and .items() are in the same order
    # http://www.python.org/dev/peps/pep-3106/
    for row in converted_data:
      question_marks = ','.join('?'*len(row.keys()))
      # This is vulnerable to injection.
      sql = "INSERT INTO %s (%s) VALUES (%s);" % (quote(table_name), ','.join(row.keys()), question_marks)
      self.execute(sql, row.values(), commit=False)

    self.__commit_if_necessary(kwargs)

  def __commit_if_necessary(self, kwargs):
    if kwargs.get('commit', self.auto_commit):
      self.commit()

  def get_var(self, key):
    "Retrieve one saved variable from the database."
    vt = quote(self.__vars_table)
    data = self.execute("SELECT * FROM %s WHERE `key` = ?" % vt, [key], commit = False)
    if data == []:
      raise NameError("The DumpTruck variables table doesn't have a value for %s." % key)
    else:
      tmp = quote(self.__vars_table_tmp)
      row = data[0]

      self.execute('DROP TABLE IF EXISTS %s' % tmp, commit = False)

      # This is vulnerable to injection
      self.execute('CREATE TABLE %s (`value` %s)' % (tmp, row['type']), commit = False)

      # This is ugly
      self.execute('INSERT INTO %s (`value`) VALUES (?)' % tmp, [row['value']], commit = False)
      value = self.dump(tmp)[0]['value']
      self.execute('DROP TABLE %s' % tmp, commit = False)

      return value

  def save_var(self, key, value, **kwargs):
    "Save one variable to the database."

    # Check whether Highwall's variables table exists
    self.__check_or_create_vars_table()

    column_type = get_column_type(value)
    tmp = quote(self.__vars_table_tmp)

    self.execute('DROP TABLE IF EXISTS %s' % tmp, commit = False)

    # This is vulnerable to injection
    self.execute('CREATE TABLE %s (`value` %s)' % (tmp, column_type), commit = False)

    # This is ugly
    self.execute('INSERT INTO %s (`value`) VALUES (?)' % tmp, [value], commit = False)
    p1 = (quote(self.__vars_table), tmp)
    p2 = [key, column_type, value]
    self.execute('''
INSERT INTO %s (`key`, `type`, `value`)
  SELECT
    ? AS key,
    ? AS type,
    value
  FROM %s
  WHERE value = ?
''' % p1, p2)
    self.execute('DROP TABLE %s' % tmp, commit = False)

    self.__commit_if_necessary(kwargs)

  def tables(self):
    result = self.execute("SELECT name FROM sqlite_master WHERE TYPE='table'", commit = False)
    return set([row['name'] for row in result])

  def drop(self, table_name = "dumptruck", **kwargs):
    "Drop a table."
    return self.execute('DROP IF EXISTS %s;' % quote(table_name), **kwargs)

  def dump(self, table_name = "dumptruck"):
    "Dump a table."
    return self.execute('SELECT * FROM %s;' % quote(table_name))

