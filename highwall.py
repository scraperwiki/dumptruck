import json

class Highwall:
  "A relaxing interface to SQLite"

  def __init__(self,dbname="highwall.db",vars_table="_highwallvars",auto_commit=True):
    pass
    # Should database changes be committed automatically after each command?
    self.AUTO_COMMIT=auto_commit

  def exec(self):
    """
    Run raw SQL on the database, and receive relaxing output.
    This is sort of the foundational method that most of the
    others build on.
    """

  def commit(self):
    "Commit database transactions."

  def save(self,data,table_name):
    pass

  def get_var(self,key):
    "Retrieve one saved variable from the database."
    return self.exec("SELECT ? FROM `%s` WHERE `key` = ?")

  def save_var(self,key,value):
    "Save one variable to the database."
    valuetype="str"
    #valuetype in ("json","unicode","str",&c)
    data={"key":key,"value":value,"type":valuetype}
    return self.save(data,

  def show_tables(self):
    return self.exec("something")

  def drop(self,table_name):
    if "`" in table_name:
      #Raise an error? Remove it?
      pass
    return self.exec('DROP IF EXISTS `%s`;' % table_name)

  #setindices
  #getindices
