from unittest import TestCase, main
from highwall import Highwall, Index
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

class TestInvalidParams(TestDb):
  "Invalid parameters should raise appropriate errors."

  def test_auto_commit(self):
    for value in (None,3,'uaoeu',set([3]),[]):
      self.assertRaises(TypeError, Highwall, auto_commit = value)

  def test_dbname(self):
    for value in (None,3,True,False,set([3]),[]):
      self.assertRaises(TypeError, Highwall, dbname = value)

  def test_dbname(self):
    "http://stackoverflow.com/questions/3694276/what-are-valid-table-names-in-sqlite"
    values = (
      'abc123', '123abc','abc_123',
      '_123abc','abc-abc','abc.abc',
      None, 3, True, False, set([3]), []
    )
    for value in values:
      self.assertRaises(Highwall.TableNameError, Highwall, dbname = value)


class TestParams(TestDb):
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
