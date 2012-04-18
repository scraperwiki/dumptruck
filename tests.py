#!/usr/bin/env python2

# Copyright 2012 Thomas Levine

# This file is part of DumpTruck.

# DumpTruck is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# DumpTruck is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.

# You should have received a copy of the GNU Affero Public License
# along with DumpTruck.  If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase, main
from json import loads, dumps
from dumptruck import DumpTruck, Pickle, quote
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
    self.assertQuote('no^[hs!\'e]?\'sf_"&\'', '`no^[hs!\'e]?\'sf_"&\'`')

class TestQuoteError(TestCase):
  "Unquotables should raise a particular ValueError."
  def assertQuoteError(self, textIn):
    self.assertRaises(ValueError, lambda: quote(textIn))

  def test_quote_error(self):
    self.assertQuoteError(']`')

class TestDb(TestCase):
  def setUp(self):
    self.cleanUp()

  def tearDown(self):
    #pass
    self.cleanUp()

  def cleanUp(self):
    "Clean up temporary files."
    for filename in ('test.db', 'dumptruck.db'):
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
#    self.h = DumpTruck(dbname = 'fixtures/absa-dumptruckvars.sqlite',vars_table="swvariables")
#
#  def test_existing_var(self):
#   self.assertEquals(self.h.get_var('DATE'),1329518937.92)
#
#  def test_nonexisting_var(self):
#   self.assertRaises(NameError,self.h.get_var,'nonexistant_var')

class SaveGetVar(TestDb):
  def savegetvar(self, var):
    h = DumpTruck(dbname = 'test.db')
    h.save_var("weird", var)
    self.assertEqual(h.get_var("weird"), var)
    h.close()

class TestSaveGetPickle(SaveGetVar):
  def test_list(self):
    self.savegetvar(Pickle({30: None}))

class TestSaveGetList(SaveGetVar):
  def test_list(self):
    self.savegetvar([])

class TestSaveGetDict(SaveGetVar):
  def test_dict(self):
    self.savegetvar({})

class TestSaveVar(TestDb):
  def setUp(self):
    self.cleanUp()
    h = DumpTruck(dbname = 'test.db')
    h.save_var("birthday","November 30, 1888")
    h.close()
    connection=sqlite3.connect('test.db')
    self.cursor=connection.cursor()

  def test_insert(self):
    self.cursor.execute("SELECT key, value, type FROM `_dumptruckvars`")
    observed = self.cursor.fetchall()
    expected = [("birthday", "November 30, 1888", "text",)]
    self.assertEqual(observed, expected)

  def test_has_some_index(self):
    """
    PRAGMA index_info(index-name);

    This pragma returns one row each column in the named index. The first column of the result is the rank of the column within the index. The second column of the result is the rank of the column within the table. The third column of output is the name of the column being indexed.

    PRAGMA index_list(table-name);

    This pragma returns one row for each index associated with the given table. Columns of the result set include the index name and a flag to indicate whether or not the index is UNIQUE.
    """
    self.cursor.execute("PRAGMA index_list(_dumptruckvars)")
    indices = self.cursor.fetchall()
#   self.assertNotEqual(indices,[])

class DumpTruckVars(TestDb):
  def save(self, key, value):
    h = DumpTruck(dbname = 'test.db')
    h.save_var(key, value)
    h.close()

  def check(self, key, value, sqltype):
    connection=sqlite3.connect('test.db')
    self.cursor=connection.cursor()
    self.cursor.execute("SELECT key, value, `type` FROM `_dumptruckvars`")
    observed = self.cursor.fetchall()
    expected = [(key, value, sqltype)]
    self.assertEqual(observed, expected)

  def get(self, key, value):
    h = DumpTruck(dbname = 'test.db')
    self.assertEqual(h.get_var(key), value)
    h.close()

  def save_check_get(self, key, value, sqltype):
    self.save(key, value)
    self.check(key, value, sqltype)
    self.get(key, value)

class TestVarsSQL(DumpTruckVars):
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
    h = DumpTruck(dbname='landbank_branches.sqlite')
    data_observed = h.execute("SELECT * FROM `branches` WHERE Fax is not null ORDER BY Fax LIMIT 3;")
    data_expected = [{'town': u'\r\nCenturion', 'date_scraped': 1327791915.618461, 'Fax': u' (012) 312 3647', 'Tel': u' (012) 686 0500', 'address_raw': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001\n (012) 686 0500\n (012) 312 3647', 'blockId': 14, 'street-address': None, 'postcode': u'\r\n0001', 'address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001', 'branchName': u'Head Office'}, {'town': u'\r\nCenturion', 'date_scraped': 1327792245.787187, 'Fax': u' (012) 312 3647', 'Tel': u' (012) 686 0500', 'address_raw': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001\n (012) 686 0500\n (012) 312 3647', 'blockId': 14, 'street-address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark', 'postcode': u'\r\n0001', 'address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001', 'branchName': u'Head Office'}, {'town': u'\r\nMiddelburg', 'date_scraped': 1327791915.618461, 'Fax': u' (013) 282 6558', 'Tel': u' (013) 283 3500', 'address_raw': u'\r\n184 Jan van Riebeeck Street\n\r\nMiddelburg\n\r\n1050\n (013) 283 3500\n (013) 282 6558', 'blockId': 17, 'street-address': None, 'postcode': u'\r\n1050', 'address': u'\r\n184 Jan van Riebeeck Street\n\r\nMiddelburg\n\r\n1050', 'branchName': u'Middelburg'}]
    self.assertListEqual(data_observed, data_expected)
    os.remove('landbank_branches.sqlite')

class TestShowTables(TestDb):
  def test_show_tables(self):
    shutil.copy('fixtures/landbank_branches.sqlite','test.db')
    h = DumpTruck(dbname = 'test.db')
    self.assertSetEqual(h.tables(),set(['blocks','branches']))

class TestCreateTable(TestDb):
  def test_create_table(self):
    h = DumpTruck(dbname = 'test.db')
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
  def save_and_check(self, dataIn, tableIn, dataOut, tableOut = None, twice = True):
    if tableOut == None:
      tableOut = quote(tableIn)

    # Insert
    h = DumpTruck(dbname = 'test.db')
    h.insert(dataIn, tableIn)
    h.close()

    # Observe with pysqlite
    connection=sqlite3.connect('test.db')
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM %s" % tableOut)
    observed1 = cursor.fetchall()
    connection.close()

    if twice:
      # Observe with DumpTruck
      h = DumpTruck(dbname = 'test.db')
      observed2 = h.execute('SELECT * FROM %s' % tableOut)
      h.close()
 
      #Check
      expected1 = dataOut
      expected2 = [dataIn] if type(dataIn) == dict else dataIn
 
      self.assertListEqual(observed1, expected1)
      self.assertListEqual(observed2, expected2)
      

class TestSaveDict(SaveAndCheck):
  def test_save_integers(self):
    d = {1: "A", 2: "B", 3: "C"}
    self.assertRaises(TypeError, lambda: self.save_and_check(
      {"modelNumber": d}
    , "model-numbers"
    , [(dumps(d),)]
    ))

  def test_save_text(self):
    d = {'1': 'A', '2': 'B', '3': 'C'}
    self.save_and_check(
      {"modelNumber": d}
    , "model-numbers"
    , [(dumps(d),)]
    )

  def test_save_fanciness(self):
    d = {'1': datetime.datetime(2012, 3, 5)}
    self.assertRaises(TypeError, lambda: self.save_and_check(
      {"modelNumber": d}
    , "model-numbers"
    , [(dumps(d),)]
    ))

class SaveAndSelect(TestDb):
  def save_and_select(self, d):
    dt = DumpTruck()
    dt.insert({"foo": d})

    observed = dt.dump()[0]['foo']
    self.assertEqual(d, observed)

class TestSaveLong1(SaveAndSelect):
  def test_zeroes(self):
    self.save_and_select(100000000000000000000000000000000)

class TestSaveLong2(SaveAndSelect):
  def test_e(self):
    self.save_and_select(1e+32)

class TestSaveBigFloat(SaveAndSelect):
  def test_save_bigfloat(self):
    self.save_and_select(1.29839287397423984729387429837492374e+100)

class TestSavePickle(SaveAndSelect):
  def test_save_pickle(self):
    import pickle
    self.save_and_select(pickle.dumps(SaveAndSelect))

#class TestSaveLambda(SaveAndSelect):
#  def test_save_lambda(self):
#    self.save_and_select(lambda x: x^2)

class TestSaveSet(SaveAndSelect):
  def test_save_set(self):
    self.save_and_select(set(["A", "B", "C"]))

class TestSaveBoolean(SaveAndCheck):
  def test_save_true(self):
    self.save_and_check(
      {"a": True}
    , "a"
    , [(1,)]
    )

  def test_save_true(self):
    self.save_and_check(
      {"a": False}
    , "a"
    , [(0,)]
    )

class TestSaveList(SaveAndCheck):
  def test_save_integers(self):
    d = ["A", "B", "C"]
    self.save_and_check(
      {"model-codes": d}
    , "models"
    , [(dumps(d),)]
    )

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
    , twice = False
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
      {"lastname":"LeTourneau"}
    , "`asoeu`"
    , [(u'LeTourneau',)]
    )

class TestSaveWeirdTableName3(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"lastname":"LeTourneau"}
    , "[asoeu]"
    , [(u'LeTourneau',)]
    )

class TestMultipleColumns(SaveAndSelect):
  def test_save(self):
    self.save_and_select({"firstname":"Robert","lastname":"LeTourneau"})

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
      {"lastname":"LeTourneau"}
    , "diesel-engineers"
    , [(u'LeTourneau',)]
    )

class TestSaveDate(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"birthday":datetime.datetime.strptime('1990-03-30', '%Y-%m-%d').date()}
    , "birthdays"
    , [(u'1990-03-30',)]
    )

class TestSaveDateTime(SaveAndCheck):
  def test_save(self):
    self.save_and_check(
      {"birthday":datetime.datetime.strptime('1990-03-30', '%Y-%m-%d')}
    , "birthdays"
    , [(u'1990-03-30 00:00:00',)]
    )

class TestInvalidDumpTruckParams(TestDb):
  "Invalid parameters should raise appropriate errors."

  def test_auto_commit(self):
    for value in (None,3,'uaoeu',set([3]),[]):
      self.assertRaises(TypeError, DumpTruck, auto_commit = value)

  def test_dbname(self):
    for value in (None,3,True,False,set([3]),[]):
      self.assertRaises(TypeError, DumpTruck, dbname = value)

  def test_vars_table_nonstr(self):
    nonstr_values = (
      None, 3, True, False, set([3]), []
    )
    for value in nonstr_values:
      self.assertRaises(TypeError, DumpTruck, vars_table = value)


class TestDumpTruckParams(TestDb):
  def test_params(self):
    self.assertFalse(os.path.isfile('test.db'))
    h = DumpTruck(dbname='test.db',auto_commit=False,vars_table="baz")
    self.assertTrue(os.path.isfile('test.db'))
#   self.assertEqual(h.auto_commit, False)
#   self.assertEqual(h.__vars_table, "baz")

class TestParamsDefaults(TestDb):
  def test_params(self):
    self.assertFalse(os.path.isfile('dumptruck.db'))
    h = DumpTruck()
    self.assertTrue(os.path.isfile('dumptruck.db'))
#   self.assertEqual(h.auto_commit, True)
#   self.assertEqual(h.__vars_table, "_dumptruckvars")

if __name__ == '__main__':
  main()
