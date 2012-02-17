from unittest import TestCase,main
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

class TestInitialize(TestDb):

class TestDefaults(TestDb):
  def test_defaults(self):
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
