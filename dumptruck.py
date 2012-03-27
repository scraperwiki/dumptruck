import json
import sqlite3
import re
import datetime
from convert import convert, quote
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
      quote(self.__vars_table)
    )

    try:
      self.execute('ALTER TABLE %s ADD COLUMN value BLOB' % quote(self.__vars_table))
    except:
      raise
    else:
      self.connection.commit()

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
    rows =self.cursor.fetchall()

    if 'commit' in kwargs and kwargs['commit']:
      self.commit()

    if None == self.cursor.description:
      return None
    else:
      colnames = [d[0] for d in self.cursor.description] 
      rawdata = [dict(zip(colnames,row)) for row in rows]
      # If I can figure out the column types, I can do this.
      # datetime.datetime.strptime(u'1990-03-30', '%Y-%m-%d').date()
      # datetime.datetime.strptime(u'1990-03-30T00:00:00', '%Y-%m-%dT%H:%M:%S')
      return rawdata

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


  def __column_types(self, table_name):
    # This is vulnerable to injection.
    self.cursor.execute("PRAGMA table_info(%s)" % quote(table_name))
    return {column[1]:column[2] for column in self.cursor.fetchall()}

  def __check_and_add_columns(self, table_name, converted_data_row):
    column_types = self.__column_types(table_name)
    for key,value in converted_data_row.items():
      try:
        column_type = "pickle text" if isinstance(value, Pickle) else PYTHON_SQLITE_TYPE_MAP[type(value)]
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

  def create_table(self, data, table_name, commit = True, error_if_exists = False):
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
      if (not re.match(r'^table.+already exists$', str(msg))) or (error_if_exists == True):
        raise
    else:
      self.connection.commit()

    for row in converted_data:
      self.__check_and_add_columns(table_name, row)


  def insert(self, data, table_name = "dumptruck", commit = True):
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
      self.execute('INSERT INTO %s (`value`) VALUES (%s)' % (tmp, row['value']), commit = False)
      value = self.dump(tmp)[0]['value']
      self.execute('DROP TABLE %s' % tmp, commit = False)
      self.commit()

      return value

  def save_var(self, key, value, commit = True):
    "Save one variable to the database."

    # Check whether Highwall's variables table exists
    self.__check_or_create_vars_table()

    data = {
      "key": key,
      "type": PYTHON_SQLITE_TYPE_MAP[type(value)],
      "value":value,
    }

    return self.insert(data, self.__vars_table, commit = commit)

  def tables(self):
    result = self.execute("SELECT name FROM sqlite_master WHERE TYPE='table'", commit = False)
    return set([row['name'] for row in result])

  def drop(self, table_name = "dumptruck", commit = True):
    "Drop a table."
    return self.execute('DROP IF EXISTS %s;' % quote(table_name), commit = commit)

  def dump(self, table_name = "dumptruck", commit = True):
    "Dump a table."
    return self.execute('SELECT * FROM %s;' % quote(table_name), commit = commit)
