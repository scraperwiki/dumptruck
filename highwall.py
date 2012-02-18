import json
import sqlite3
from copy import copy

class Index:
  COLNAME_TYPES = set([unicode, str, int])

  class MineCollapse(Exception):
    pass

  class TableNameError(self.MineCollapse):
    pass

  class DuplicateColumnError(self.MineCollapse):
    pass

  class InvalidTableName(self.MineCollapse):
    pass

  class ColumnNameError(self.MineCollapse):
    pass

  class EncodingError(self.MineCollapse):
    pass


  def __init__(self, columns, unique = False):
    self.unique = unique
    if type(columns) in self.COLNAME_TYPES:
      # One column
      self.__columns = [str(columns)]
    elif set(map(type, columns)).issubset(self.COLNAME_Types):
      # Multiple columns
      str_columns = map(str, columns)
      if len(set(str_columns)) != len(columns):
        raise self.DuplicateColumnError
      else:
        self.__columns = str_columns

class Highwall:
  "A relaxing interface to SQLite"

  def __init__(self, dbname = "highwall.db", vars_table = "_highwallvars", auto_commit = True):
    pass
    # Should database changes be committed automatically after each command?
    self.auto_commit = auto_commit

    # Database connection
    self.connection=sqlite3.connect(dbname)
    self.cursor=self.connection.cursor()

    # Make sure it's a good table name
    self.__check_table_name(vars_table)

  @staticmethod
  def __check_table_name(table_name):
    "Check that the table name has no quote character. Raise an error if it does."
    if "`" in table_name:
      #Raise an error? Remove it?
      raise self.InvalidTableName

  def __check_or_create_vars_table(self):
    if self.__vars_table in self.show_tables():
      pass #Do something
    else:
      self.__check_table_name(self.__vars_table)
      self.cursor.execute("""
        CREATE TABLE `%s` (
          key TEXT,
          value BLOB,
          type TEXT
        );""" % self.__vars_table)

  def execute(self, sql, commit = True, *args, **kwargs):
    """
    Run raw SQL on the database, and receive relaxing output.
    This is sort of the foundational method that most of the
    others build on.
    """
    self.cursor.execute(sql, *args, **kwargs)
    colnames = [d[0] for d in self.cursor.description] 
    rows =self.cursor.fetchall()

    if commit:
      self.commit()

    if rows==None:
      return None
    else:
      return [dict(zip(colnames,row)) for row in rows]

  def commit(self):
    "Commit database transactions."
    return self.connection.commit()

  def close(self):
    return self.connection.close()

  def save(self, data, table_name, commit = True):

    # Allow single rows to be dictionaries.
    if type(data)==dict:
      data = [data]

    # http://stackoverflow.com/questions/1952464/
    # in-python-how-do-i-determine-if-a-variable-is-iterable
    try:
      set([ type(e) for e in my_object])==set([dict])
    except TypeError:
      raise TypeError('The data argument must be a dict or an iterable of dicts.')

    conved_data = [DataDump(row).dump() for row in data]
    
    # .keys() and .items() are in the same order
    # http://www.python.org/dev/peps/pep-3106/
    for row in conved_data:
      question_marks = ','.join('?'*len(row.keys()))
      sql = "INSERT INTO `%s`(%s) VALUES (%s);" % (table_name, question_marks, question_marks)
      self.execute(sql, (row.keys(), row.values()) ,commit=False)
    self.commit()

  def get_var(self, key):
    "Retrieve one saved variable from the database."
    return self.execute("SELECT ? FROM `%s` WHERE `key` = ?", key, commit = False)

  def save_var(self, key, value, commit = True):
    "Save one variable to the database."

    # Check whether Highwall's variables table exists
    self.__vars_table = vars_table
    self.__check_or_create_vars_table()

    # Prepare for save
    valuetype = "str" #This is a lie.
    #valuetype in ("json", "unicode", "str", &c)
    data = {"name":key, "value_blob":value, "type":valuetype}

    return self.save(data, self.__vars_table, commit = commit)

  def show_tables(self):
    result = self.execute("SELECT name FROM sqlite_master WHERE TYPE='table'", commit = False)
    return set([row['name'] for row in result])

  def drop(self, table_name, commit = True):
    self.__check_table_name(table_name)
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
    for key self.data.keys():
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
