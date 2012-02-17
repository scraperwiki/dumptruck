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

class TestSave(TestDb):
  def test_foo_bar(self):
    pass

if __name__ == '__main__':
  main()
