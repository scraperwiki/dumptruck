import json
import sqlite3
import re
import datetime
from convert import convert, quote

# Mappings between Python types and SQLite types
SQLITE_PYTHON_TYPE_MAP={
  u"text": unicode,
  u"integer": int,
  u"bool": bool,
  u"real": float,
  u"date": datetime.date,
  u"datetime": datetime.datetime,
  #u"null": ??
  #BLOB: ??? The value is a blob of data, stored exactly as it was input.
}

PYTHON_SQLITE_TYPE_MAP={
  unicode: u"text",
  str: u"text",

  int: u"integer",
  long: u"integer",
  bool: u"boolean",

  float: u"real",
  datetime.date: u"date",
  datetime.datetime: u"datetime",
}

# Only for compatibility with scraperwiki;
# we should use the SQLite names
#SWVARIABLES_PYTHON_TYPE_MAP={
#  u"float": float
#}

class Highwall:
  "A relaxing interface to SQLite"

  def __init__(self, dbname = "highwall.db", vars_table = "_highwallvars", auto_commit = True):
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
      self.connection=sqlite3.connect(dbname)
      self.cursor=self.connection.cursor()

    # Make sure it's a good table name
    if type(vars_table) not in [unicode, str]:
      raise TypeError("vars_table must be a string")
    else:
      self.__vars_table = vars_table

  def __check_or_create_vars_table(self):
    try:
      # This is vulnerable to injection.
      self.cursor.execute("""
        CREATE TABLE `%s` (
          name TEXT,
          value_blob BLOB,
          sql_type TEXT,
          lang TEXT,
          lang_type TEXT
        );""" % self.__vars_table)
    except:
      raise
    else:
      self.connection.commit()

  def execute(self, sql, *args, **kwargs):
    """
    Run raw SQL on the database, and receive relaxing output.
    This is sort of the foundational method that most of the
    others build on.
    """
    self.cursor.execute(sql, *args)
    rows =self.cursor.fetchall()

    if 'commit' in kwargs and kwargs['commit']:
      self.commit()

    if None == self.cursor.description:
      return None
    else:
      colnames = [d[0] for d in self.cursor.description] 
      return [dict(zip(colnames,row)) for row in rows]

  def commit(self):
    "Commit database transactions."
    return self.connection.commit()

  def close(self):
    return self.connection.close()

  def create_unique_index(table_name, columns):
    self.create_index(table_name, columns, unique = True)

  def create_index(table_name, columns, unique = False):
    "Create a unique index on the column(s) passed."
    index_name = table_name + '__' + '_'.join(columns)
    arbitrary_number = 0
    while True:
      try:
        # This is vulnerable to injection.
        if unique:
          sql = "CREATE UNIQUE INDEX ? ON %s (%s)"
        else:
          sql = "CREATE INDEX ? ON %s (%s)"
        self.execute(sql % (quote(table_name), ','.join(columns)), index_name+str(arbitrary_number))
      except:
        arbitrary_number += 1

  def __add_column(self, table_name, column_name, column_type):
    # This is vulnerable to injection.
    sql = 'ALTER TABLE %s ADD COLUMN %s %s ' % (table_name, column_name, column_type)
    self.execute(sql, commit = True)

  def __column_types(self, table_name):
    # This is vulnerable to injection.
    self.cursor.execute("PRAGMA table_info(%s)" % quote(table_name))
    return {column[1]:column[2] for column in self.cursor.fetchall()}

  def __check_and_add_columns(self, table_name, converted_data_row):
    column_types = self.__column_types(table_name)
    for key,value in converted_data_row.items():
      try:
        self.__add_column(quote(table_name), key, PYTHON_SQLITE_TYPE_MAP[type(value)])
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

  def create_table(self, data, table_name, commit = True):
    "Create a table based on the data, but don't insert anything."
    converted_data = convert(data)
    startdata = converted_data[0]

    # Select a non-null item
    for k, v in startdata.items():
      if v != None:
        break

    try:
      # This is vulnerable to injection.
      self.cursor.execute("""
        CREATE TABLE %s (
          %s %s
        );""" % (quote(table_name), quote(k), PYTHON_SQLITE_TYPE_MAP[type(startdata[k])]))
    except sqlite3.OperationalError, msg:
      if not re.match(r'^table.+already exists$', str(msg)):
        raise
    else:
      self.connection.commit()

    for row in converted_data:
      self.__check_and_add_columns(table_name, row)


  def insert(self, data, table_name, commit = True):
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
    self.commit()

  def get_var(self, key):
    "Retrieve one saved variable from the database."
    # This is vulnerable to injection.
    data = self.execute("SELECT * FROM %s WHERE `name` = ?" % quote(self.__vars_table), [key], commit = False)
    if data == []:
      raise NameError("The Highwall variables table doesn't have a value for %s." % key)
    else:
      row = data[0]
      if row.has_key('sql_type') and SQLITE_PYTHON_TYPE_MAP.has_key(row['sql_type']):
        cast = SQLITE_PYTHON_TYPE_MAP[row['sql_type']]
      else:
        raise TypeError("A Python type for '%s' could not be found." % row['type'])
      return cast(row['value_blob'])

  def save_var(self, key, value, commit = True):
    "Save one variable to the database."

    # Check whether Highwall's variables table exists
    self.__check_or_create_vars_table()

    # Prepare for save
    if type(value) in PYTHON_SQLITE_TYPE_MAP:
      sqltype = PYTHON_SQLITE_TYPE_MAP[type(value)]
      lang = None
      langtype = None
    elif type(value) in PYTHON_JSON_TYPE_MAP:
      sqltype = None
      langtype = PYTHON_JSON_TYPE_MAP[type(value)]
      lang = 'json'
    elif type(value) in PYTHON_PYTHON_TYPE_MAP:
      sqltype = None
      langtype = PYTHON_PYTHON_TYPE_MAP[type(value)]
      lang = 'python'

    #valuetype in ("json", "unicode", "str", &c)
    data = {
      "name":key, "value_blob":value,
      "sql_type":sqltype,
      "lang": lang, "lang_type": langtype
    }

    return self.insert(data, self.__vars_table, commit = commit)

  def tables(self):
    result = self.execute("SELECT name FROM sqlite_master WHERE TYPE='table'", commit = False)
    return set([row['name'] for row in result])

  def drop(self, table_name, commit = True):
    # This is vulnerable to injection.
    return self.execute('DROP IF EXISTS %s;' % quote(table_name), commit = commit)
