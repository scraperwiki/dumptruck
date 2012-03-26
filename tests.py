from unittest import TestCase, main
from highwall import Highwall
from convert import quote
import sqlite3
import os, shutil
import datetime

class TestQuote(TestCase):
  def assertQuote(self, textIn, textOut):
    self.assertEqual(quote(textIn), textOut)

  def test_quote(self):
    self.assertQuote('a','`a`')

    self.assertQuote('[','`[`')
    self.assertQuote('`','[`]')
    self.assertQuote('"','`"`')
    self.assertQuote('\'','`\'`')

    self.assertQuote('[aoeu]','[aoeu]')

    self.assertQuote('ao 98!?o-_Ho[e&((*^ueu','`ao 98!?o-_Ho[e&((*^ueu`')
    self.assertQuote('ao 98!?o-_H`oe&((*^ueu','[ao 98!?o-_H`oe&((*^ueu]')

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
        pass
#       if (2, 'No such file or directory')!=e:
#         raise

#Move this to a ScraperWiki drop-in replacement library.
#class TestGetVar(TestDb):
#  def setUp(self):
#    self.cleanUp()
#    self.h = Highwall(dbname = 'fixtures/absa-highwallvars.sqlite',vars_table="swvariables")
#
#  def test_existing_var(self):
#   self.assertEquals(self.h.get_var('DATE'),1329518937.92)
#
#  def test_nonexisting_var(self):
#   self.assertRaises(NameError,self.h.get_var,'nonexistant_var')

class TestSaveVar(TestDb):
  def setUp(self):
    self.cleanUp()
    h = Highwall(dbname = 'test.db')
    h.save_var("birthday","November 30, 1888")
    h.close()
    connection=sqlite3.connect('test.db')
    self.cursor=connection.cursor()

  def test_insert(self):
    self.cursor.execute("SELECT name, value_blob, sql_type, lang, lang_type FROM `_highwallvars`")
    observed = self.cursor.fetchall()
    expected = [("birthday", "November 30, 1888", "text", None, None)]
    self.assertEqual(observed, expected)

  def test_has_some_index(self):
    """
    PRAGMA index_info(index-name);

    This pragma returns one row each column in the named index. The first column of the result is the rank of the column within the index. The second column of the result is the rank of the column within the table. The third column of output is the name of the column being indexed.

    PRAGMA index_list(table-name);

    This pragma returns one row for each index associated with the given table. Columns of the result set include the index name and a flag to indicate whether or not the index is UNIQUE.
    """
    self.cursor.execute("PRAGMA index_list(_highwallvars)")
    indices = self.cursor.fetchall()
#   self.assertNotEqual(indices,[])

class TestVars(TestDb):
  def save(self, key, value):
    h = Highwall(dbname = 'test.db')
    h.save_var(key, value)
    h.close()

  def check(self, key, value, sqltype, lang = None, langtype = None):
    connection=sqlite3.connect('test.db')
    self.cursor=connection.cursor()
    self.cursor.execute("SELECT name, value_blob, `sql_type`, `lang`, `lang_type` FROM `_highwallvars`")
    observed = self.cursor.fetchall()
    expected = [(key, value, sqltype, lang, langtype)]
    self.assertEqual(observed, expected)

  def get(self, key, value):
    h = Highwall(dbname = 'test.db')
    self.assertEqual(h.get_var(key), value)
    h.close()

  def save_check_get(self, key, valueIn, sqltype, lang = None, langtype = None, valueOut = None):
    if valueOut == None:
      valueOut = valueIn

    self.save(key, valueIn)
    self.check(key, valueOut, sqltype, lang, langtype = langtype)
    self.get(key, valueOut)

class TestVarsSQL(TestVars):
  def test_integer(self):
    self.save_check_get('foo', 42, 'integer')

#class TestVarsJSON(TestVars):
#  def test_list(self):
#    self.save_check_get('foo', [], 'text')
#  def test_dict(self):
#    self.save_check_get('foo', {}, 'text')

#class TestVarsPickle(TestVars):
#  def test_func(self):
#    y = lambda x: x^2
#    self.save_check_get('foo', y, 'blob')

class TestSelect(TestDb):
  def test_select(self):
    shutil.copy('fixtures/landbank_branches.sqlite','.')
    h = Highwall(dbname='landbank_branches.sqlite')
    data_observed = h.execute("SELECT * FROM `branches` WHERE Fax is not null ORDER BY Fax LIMIT 3;")
    data_expected = [{'town': u'\r\nCenturion', 'date_scraped': 1327791915.618461, 'Fax': u' (012) 312 3647', 'Tel': u' (012) 686 0500', 'address_raw': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001\n (012) 686 0500\n (012) 312 3647', 'blockId': 14, 'street-address': None, 'postcode': u'\r\n0001', 'address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001', 'branchName': u'Head Office'}, {'town': u'\r\nCenturion', 'date_scraped': 1327792245.787187, 'Fax': u' (012) 312 3647', 'Tel': u' (012) 686 0500', 'address_raw': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001\n (012) 686 0500\n (012) 312 3647', 'blockId': 14, 'street-address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark', 'postcode': u'\r\n0001', 'address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001', 'branchName': u'Head Office'}, {'town': u'\r\nMiddelburg', 'date_scraped': 1327791915.618461, 'Fax': u' (013) 282 6558', 'Tel': u' (013) 283 3500', 'address_raw': u'\r\n184 Jan van Riebeeck Street\n\r\nMiddelburg\n\r\n1050\n (013) 283 3500\n (013) 282 6558', 'blockId': 17, 'street-address': None, 'postcode': u'\r\n1050', 'address': u'\r\n184 Jan van Riebeeck Street\n\r\nMiddelburg\n\r\n1050', 'branchName': u'Middelburg'}]
    self.assertListEqual(data_observed, data_expected)
    os.remove('landbank_branches.sqlite')

class TestShowTables(TestDb):
  def test_show_tables(self):
    shutil.copy('fixtures/landbank_branches.sqlite','test.db')
    h = Highwall(dbname = 'test.db')
    self.assertSetEqual(h.tables(),set(['blocks','branches']))

class TestCreateTable(TestDb):
  def test_create_table(self):
    h = Highwall(dbname = 'test.db')
    h.create_table({"foo": 0, "bar": 1, "baz": 2}, 'zombies')
    h.close()

    connection=sqlite3.connect('test.db')
    cursor=connection.cursor()
    cursor.execute("SELECT foo, bar, baz FROM zombies")
    observed = cursor.fetchall()
    connection.close()

    expected = []
    self.assertListEqual(observed, expected)

class SaveAndCheck(TestDb):
  def save_and_check(self, dataIn, tableIn, dataOut, tableOut = None):
    if tableOut == None:
      tableOut = quote(tableIn)

    h = Highwall(dbname = 'test.db')
    h.insert(dataIn, tableIn)
    h.close()

    connection=sqlite3.connect('test.db')
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM %s" % tableOut)
    observed = cursor.fetchall()
    connection.close()

    expected = dataOut
    self.assertListEqual(observed, expected)

class TestSaveTwice(SaveAndCheck):
  def test_save_twice(self):
    self.save_and_check(
      {"modelNumber": 293}
    , "model-numbers"
    , [(293,)]
    )
    self.save_and_check(
      {"modelNumber": 293}
    , "model-numbers"
    , [(293,), (293,)]
    )

class TestSaveInt(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"modelNumber": 293}
    , "model-numbers"
    , [(293,)]
    )

class TestSaveWeirdTableName1(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"modelNumber": 293}
    , "This should-be a_valid.table+name!?"
    , [(293,)]
    )

class TestSaveWeirdTableName2(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"firstname":"Robert","lastname":"LeTourneau"}
    , "`asoeu`"
    , [(u'LeTourneau', u'Robert')]
    )

class TestSaveWeirdTableName3(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"firstname":"Robert","lastname":"LeTourneau"}
    , "[asoeu]"
    , [(u'LeTourneau', u'Robert')]
    )

class TestSaveHyphen(SaveAndCheck):
  def test_save_int(self):
    self.save_and_check(
      {"model-number": 293}
    , "model-numbers"
    , [(293,)]
    )

class TestSaveString(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"firstname":"Robert","lastname":"LeTourneau"}
    , "diesel-engineers"
    , [(u'LeTourneau', u'Robert')]
    )

class TestSave(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"birthday":datetime.datetime.strptime('1990-03-30', '%Y-%m-%d').date()}
    , "birthdays"
    , [(u'1990-03-30')]
    )

class TestInvalidHighwallParams(TestDb):
  "Invalid parameters should raise appropriate errors."

  def test_auto_commit(self):
    for value in (None,3,'uaoeu',set([3]),[]):
      self.assertRaises(TypeError, Highwall, auto_commit = value)

  def test_dbname(self):
    for value in (None,3,True,False,set([3]),[]):
      self.assertRaises(TypeError, Highwall, dbname = value)

# def test_vars_table_str(self):
#   "http://stackoverflow.com/questions/3694276/what-are-valid-table-names-in-sqlite"
#   str_values = (
#     'abc123', '123abc','abc_123',
#     '_123abc','abc-abc','abc.abc',
#   )
#   for value in str_values:
#     self.assertRaises(Highwall.TableNameError, Highwall, vars_table = value)

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
#   self.assertEqual(h.auto_commit, False)
#   self.assertEqual(h.__vars_table, "baz")

class TestParamsDefaults(TestDb):
  def test_params(self):
    self.assertFalse(os.path.isfile('highwall.db'))
    h = Highwall()
    self.assertTrue(os.path.isfile('highwall.db'))
#   self.assertEqual(h.auto_commit, True)
#   self.assertEqual(h.__vars_table, "_highwallvars")

if __name__ == '__main__':
  main()
