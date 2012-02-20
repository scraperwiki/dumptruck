import json
import sqlite3
from copy import copy
import re
import datetime

# Mappings between Python types and SQLite types
SQLITE_PYTHON_TYPE_MAP={
  u"text": unicode,
  u"integer": int,
  u"real": float,
}

# Only for compatibility with scraperwiki;
# we should use the SQLite names
SWVARIABLES_PYTHON_TYPE_MAP={
  u"float": float
}

PYTHON_SQLITE_TYPE_MAP={
  unicode: u"text",
  str: u"text",
  int: u"integer",
  float: u"real",
}

class IndexList:
  'Like running `PRAGMA index_list(?);`'
  def __init__(self,highwall_object):
    self.h = highwall_object

  def __getitem__(self, table_name):
    "Retrive the indices for a table."
    return IndexInfo(self.h, table_name)

  def __setitem__(self, index_info):
    "I don't think this will ever be implemented."
    print "This should not run."

class IndexInfo:
  'Like running `PRAGMA index_info(?);`'

  class IndexNameError(Exception):
    pass

  def __init__(self,highwall_object, table_name):
    self.h = highwall_object
    self.table_name = table_name
    self.table_indices = self.h.execute("PRAGMA index_list(`%s`)" % table_name, commit = False)

  def __getitem__(self, index_name):
    "Retrive an index."
    index = self.h.execute("PRAGMA index_info(`%s`)" % index_name, commit = False)

    # Determine whether it's unique.
    for i in self.table_indices:
      if i['name'] == index_name:
        unique = i['unique']
        break

    try:
      unique
    except NameError:
      raise self.IndexNameError('There is no index with the name "%s".' % index_name)

    return Index([col['name'] for col in index], unique = unique)

  def __setitem__(self, index_name, index):
    # This is currently a bit vulnerable to injection.
    sql = "CREATE %s INDEX IF NOT EXISTS `%s` ON `%s` (%s)"
    indexed_columns = ','.join(index.columns)
    str_unique = 'UNIQUE' if index.unique else ''
    self.h.execute(sql % (str_unique, index_name, self.table_name, indexed_columns))

class Index:
  "An index absent of a table"

  #COLNAME_TYPES = set([unicode, str, int, IndexedColumn])
  COLNAME_TYPES = set([unicode, str, int])

  class DuplicateColumnError(Exception):
    pass

  def __init__(self, columns, unique = False):
    self.unique = unique

    # Set columns
    if type(columns) in self.COLNAME_TYPES:
      # One column
      self.columns = [str(columns)]
    elif set(map(type, columns)).issubset(self.COLNAME_TYPES):
      # Multiple columns
      str_columns = map(str, columns)
      if len(set(str_columns)) != len(columns):
        raise self.DuplicateColumnError
      else:
        self.columns = str_columns

class IndexedColumn:
  "This is how you do COLLATE or ASC."

  def __init__(self, collate = None, sort = None):
    self.collate = collate
    self.sort = sort
    raise NotImplementedError("IndexedColumn doesn't work yet.")

class MineCollapse(Exception):
  pass

class Highwall:
  "A relaxing interface to SQLite"

  class NameError(NameError):
    pass

  class TableNameError(MineCollapse):
    pass

  class ColumnNameError(MineCollapse):
    pass

  class EncodingError(MineCollapse):
    pass

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
      raise TypeError("auto_commit must be a string")
    else:
      self.__vars_table = vars_table

    # The index list
    self.index_list = IndexList(self)

  def __check_or_create_table(self, table_name):
    if self.__is_table(table_name):
      pass #Do something
    else:
      self.cursor.execute("""
        CREATE TABLE `%s` (
          ROWID INTEGER PRIMARY KEY
        );""" % table_name)
      self.connection.commit()

  def __check_or_create_vars_table(self):
    if self.__vars_table in self.show_tables():
      pass #Do something
    else:
      self.__is_table(self.__vars_table)
      self.cursor.execute("""
        CREATE TABLE `%s` (
          name TEXT,
          value_blob BLOB,
          type TEXT
        );""" % self.__vars_table)
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


  def __add_column(self, table_name, column_name, column_type):
    sql = 'ALTER TABLE `%s` ADD COLUMN %s %s ' % (table_name, column_name, column_type)
    self.execute(sql, commit = True)

  def __column_types(self, table_name):
    self.cursor.execute("PRAGMA table_info(`%s`)" % table_name)
    return {column[1]:column[2] for column in self.cursor.fetchall()}

  def __is_table(self,table_name):
    return table_name in self.show_tables()

  def __check_and_add_columns(self, table_name, conved_data_row):
    column_types = self.__column_types(table_name)
    for key,value in conved_data_row.items():
      if key not in column_types:
        #raise NotImplementedError("Pretend this alters the table to add the column.")
        self.__add_column(table_name, key, PYTHON_SQLITE_TYPE_MAP[type(value)])

  def __cast_data_to_column_type(self, data):
    column_types = self.__column_types(table_name)
    for key,value in data.items():
      if SQLITE_TYPE_MAP[type(key)] != column_types[key]:
        try:
          data[key] = type(key)(value)
        except ValueError:
          raise TypeError("Data could not be converted to match the existing `%s` column type.")

  def insert(self, data, table_name, commit = True):

    # Allow single rows to be dictionaries.
    if type(data)==dict:
      data = [data]

    # http://stackoverflow.com/questions/1952464/
    # in-python-how-do-i-determine-if-a-variable-is-iterable
    try:
      set([ type(e) for e in data])==set([dict])
    except TypeError:
      raise TypeError('The data argument must be a dict or an iterable of dicts.')

    self.__check_or_create_table(table_name)

    conved_data = [DataDump(row).dump() for row in data]
    for row in conved_data:
      self.__check_and_add_columns(table_name, row)
    
    # .keys() and .items() are in the same order
    # http://www.python.org/dev/peps/pep-3106/
    for row in conved_data:
      question_marks = ','.join('?'*len(row.keys()))
      sql = "INSERT INTO `%s` (%s) VALUES (%s);" % (table_name, ','.join(row.keys()), question_marks)
      self.execute(sql, row.values(), commit=False)
    self.commit()

  class HighwallVarsError(MineCollapse):
    pass

  def get_var(self, key):
    "Retrieve one saved variable from the database."
    data = self.execute("SELECT * FROM `%s` WHERE `name` = ?" % self.__vars_table, [key], commit = False)
    if data == []:
      raise self.NameError("The Highwall variables table doesn't have a value for %s." % key)
    else:
      row = data[0]
      if SQLITE_PYTHON_TYPE_MAP.has_key(row['type']):
        cast = SQLITE_PYTHON_TYPE_MAP[row['type']]
      elif SWVARIABLES_PYTHON_TYPE_MAP.has_key(row['type']):
        cast = SWVARIABLES_PYTHON_TYPE_MAP[row['type']]
      else:
        raise self.HighwallVarsError("A Python type for '%s' could not be found." % row['type'])
      return cast(row['value_blob'])

  def save_var(self, key, value, commit = True):
    "Save one variable to the database."

    # Check whether Highwall's variables table exists
    self.__check_or_create_vars_table()

    # Prepare for save
    valuetype = PYTHON_SQLITE_TYPE_MAP[type(value)]
    #valuetype in ("json", "unicode", "str", &c)
    data = {"name":key, "value_blob":value, "type":valuetype}

    return self.insert(data, self.__vars_table, commit = commit)

  def show_tables(self):
    result = self.execute("SELECT name FROM sqlite_master WHERE TYPE='table'", commit = False)
    return set([row['name'] for row in result])

  def drop(self, table_name, commit = True):
    return self.execute('DROP IF EXISTS `%s`;' % table_name, commit = commit)

class DataDump:
  "A data dictionary converter"
  def __init__(self, data):
    self.raw = data

  def dump(self):
    self.data = copy(self.raw)
    self.checkdata()
    self.jsonify()
    self.convdata()
    return self.data

  class CouldNotJSONify(Exception):
    pass

  def jsonify(self):
    for key, value in self.data.items():
      if type(value)==set:
        # Convert sets to dicts
        self.data[key] = dict(zip( list(value), [None]*len(value) ))

      if type(value) in (list, dict):
        try:
          value = dumps(value)
        except TypeError:
          raise CouldNotJSONify("The value for %s is a complex object that could not be dumped to JSON.")

  def checkdata(self):
    #Based on scraperlibs
    for key in self.data.keys():
      if not key:
        raise self.ColumnNameError('key must not be blank')
      elif type(key) not in (unicode, str):
        raise self.ColumnNameError('key must be string type')
      elif not re.match("[a-zA-Z0-9_\- ]+$", key):
        raise self.ColumnNameError('key must be simple text')

  def convdata(self):
    #Based on scraperlibs
    jdata = {}
    for key, value in self.data.items():
      if type(value) == datetime.date:
        value = value.isoformat()
      elif type(value) == datetime.datetime:
        if value.tzinfo is None:
          value = value.isoformat()
        else:
          value = value.astimezone(pytz.timezone('UTC')).isoformat()
          assert "+00:00" in value
          value = value.replace("+00:00", "")
      elif value == None:
        pass
      elif type(value) == str:
        try:
          value = value.decode("utf-8")
        except:
          raise self.EncodingError("Binary strings must be utf-8 encoded")
      elif type(value) not in [int, bool, float, unicode, str]:
        value = unicode(value)
      jdata[key] = value
    self.data = jdata
