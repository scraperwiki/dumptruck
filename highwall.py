import json
import sqlite3

class Index:
  COLNAME_TYPES = set([unicode, str, int])

  class TableNameError(Exception):
    pass

  class DuplicateColumnError(Exception):
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

  class InvalidTableName(Exception):
    pass

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
    return self.execute("--;", commit = commit)

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
