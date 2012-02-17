import json

class Highwall:
  "A relaxing interface to SQLite"

  def __init__(self,dbname="highwall.db",vars_table="_highwallvars",auto_commit=True):
    pass
    # Should database changes be committed automatically after each command?
    self.auto_commit=auto_commit
    self.__vars_table=vars_table

  def exec(self,quoted,commit=True):
    """
    Run raw SQL on the database, and receive relaxing output.
    This is sort of the foundational method that most of the
    others build on.
    """
    out = None
    if commit:
      commit
    return out

  def commit(self):
    "Commit database transactions."

  def save(self,data,table_name,commit=True):
    pass
    return self.exec("",commit=False)

  def get_var(self,key):
    "Retrieve one saved variable from the database."
    return self.exec("SELECT ? FROM `%s` WHERE `key` = ?",key,commit=False)

  def save_var(self,key,value,commit=True):
    "Save one variable to the database."
    valuetype="str" #This is a lie.
    #valuetype in ("json","unicode","str",&c)
    data={"key":key,"value":value,"type":valuetype}
    return self.save(data,self.__vars_table, commit=commit)

  def show_tables(self):
    return self.exec(".tables",commit=False)

  def drop(self,table_name,commit=True):
    if "`" in table_name:
      #Raise an error? Remove it?
      pass
    return self.exec('DROP IF EXISTS `%s`;' % table_name, commit=commit)
