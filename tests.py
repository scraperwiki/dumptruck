from unittest import TestCase, main
from highwall import Highwall, Index
import sqlite3
import os

class TestDb(TestCase):
  def setUp(self):
    self.cleanUp()

  def tearDown(self):
    self.cleanUp()

  def cleanUp(self):
    "Clean up temporary files."
    for filename in ('test.db', 'highwall.db'):
      try:
        os.remove(filename)
      except OSError as e:
        if (2, 'No such file or directory')!=e:
          raise

class TestGetVar(TestDb):
  def setUp(self):
    self.cleanup()
    self.h = Highwall(dbname = 'fixtures/absa-highwallvars.sqlite',vars_table="swvariables")

  def test_existing_var(self):
   self.assertEquals(h.get_var('DATE'),1329518937.92)

  def test_nonexisting_var(self):
   self.assertRaises(Highwall.NameError,h.get_var,'nonexistant_var')

class TestSaveVar(TestDb):
  def test_save(self):
    h = Highwall()
    h.save_var('foo','bar')
    h.close()
    connection=sqlite3.connect('test.db')
    cursor=connection.cursor()
    cursor.execute('SELECT * FROM `_highwallvars`')
    print cursor.fetchall()

class TestSaveVar(TestDb):
  def test_save(self):
    self.h = Highwall(dbname = 'fixtures/absa-highwallvars.sqlite',vars_table="swvariables")

class TestSelect(TestDb):
  def setUp(self):
    self.cleanUp()
    connection=sqlite3.connect('test.db')
    cursor=connection.cursor()
    cursor.execute(open('fixtures/testinsert.sql').read())
    connection.commit()
    connection.close()
    self.h = Highwall(dbname='test.db')

  def test_count(self):
    data = self.h.exec('SELECT * FROM `bar`')
    self.assertEqual(len(data),12)

  def test_data(self):
    h = Highwall(dbname='test.db')
    data_observed = self.h.exec('SELECT * FROM `bar`')
    f = open('fixtures/testinsert.json')
    data_expected = loads(f.read())
    f.close()
    self.assertListEqual(data_observed,data_expected)

class TestInvalidHighwallParams(TestDb):
  "Invalid parameters should raise appropriate errors."

  def test_auto_commit(self):
    for value in (None,3,'uaoeu',set([3]),[]):
      self.assertRaises(TypeError, Highwall, auto_commit = value)

  def test_dbname(self):
    for value in (None,3,True,False,set([3]),[]):
      self.assertRaises(TypeError, Highwall, dbname = value)

  def test_vars_table_str(self):
    "http://stackoverflow.com/questions/3694276/what-are-valid-table-names-in-sqlite"
    str_values = (
      'abc123', '123abc','abc_123',
      '_123abc','abc-abc','abc.abc',
    )
    for value in str_values:
      self.assertRaises(Highwall.TableNameError, Highwall, vars_table = value)

  def test_vars_table_nonstr(self):
    nonstr_values = (
      None, 3, True, False, set([3]), []
    )
    for value in nonstr_values:
      self.assertRaises(TypeError, Highwall, vars_table = value)


class TestHighwallParams(TestDb):
  def test_params(self):
    self.assertFalse(os.path.isfile('test.db'))
    h = Highwall(dbname='test.db',auto_commit=False,vars_table="baz")
    self.assertTrue(os.path.isfile('test.db'))
    self.assertEqual(h.auto_commit, False)
    self.assertEqual(h.__vars_table, "baz")

class TestParamsDefaults(TestDb):
  def test_params(self):
    self.assertFalse(os.path.isfile('highwall.db'))
    h = Highwall()
    self.assertTrue(os.path.isfile('highwall.db'))
    self.assertEqual(h.auto_commit, True)
    self.assertEqual(h.__vars_table, "_highwallvars")

class TestSave(TestDb):
  def test_foo_bar(self):
    pass

if __name__ == '__main__':
  main()
