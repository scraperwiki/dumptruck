#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

# This file is part of DumpTruck.

# Copyright (C) 2012 ScraperWiki Ltd. and other contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from collections import OrderedDict
from unittest import TestCase, main
from json import dumps
from dumptruck import DumpTruck
import sqlalchemy
import sqlite3
import os, shutil
import datetime
import lxml.etree, lxml.html

DB_FILE_MEMORY = ':memory:'
DB_FILE_TMP = '/tmp/test.db'

class TestUnicode(TestCase):
    def test_unicode_insert(self):
        import dumptruck
        dt = dumptruck.DumpTruck(DB_FILE_MEMORY)
        dt.create_table({'a': 1}, u'\u1234')
        dt.insert(table_name=u'\u1234', data={'a': 1})
        dt.insert(table_name=u'\u1234', data={'a': 1})

class TestDb(TestCase):
    def setUp(self):
        self.cleanUp()

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        'Clean up temporary files.'
        for filename in (DB_FILE_MEMORY, 'dumptruck.db'):
            try:
                os.remove(filename)
            except OSError as e:
                pass

class TestQuoting(TestDb):
    def test_question_mark(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.execute('CREATE TABLE foo (bar TEXT)')
        dt.execute('INSERT INTO foo(bar) VALUES (?)', ['baz'])
        observed = [row['bar'] for row in dt.execute('SELECT bar from foo')]
        self.assertListEqual(observed, ['baz'])

class TestDump(TestDb):
    def test_dump_nonexistant(self):
        h = DumpTruck(dbname = DB_FILE_MEMORY)
        self.assertRaises(sqlalchemy.exc.OperationalError, h.dump)

    def test_save(self):
        h = DumpTruck(dbname = DB_FILE_MEMORY)
        data = [{'firstname': 'Robert', 'lastname': 'LeTourneau'}]
        h.create_table(data, 'foo')
        h.insert(data, 'foo')
        self.assertEqual(data, h.dump('foo'))
        h.close()

class TestDrop(TestDb):
    def test_drop_nonexistant(self):
        h = DumpTruck(dbname = DB_FILE_MEMORY)
        self.assertRaises(sqlalchemy.exc.OperationalError, h.drop_table)

    def test_drop_nonexistant_if_exists(self):
        h = DumpTruck(dbname = DB_FILE_MEMORY)
        h.drop_table(if_exists = True)

    def test_save(self):
        h = DumpTruck(dbname = DB_FILE_MEMORY)
        h.create_table({'firstname': 'Robert', 'lastname': 'LeTourneau'}, 'foo')
        h.insert({'firstname': 'Robert', 'lastname': 'LeTourneau'}, 'foo')
        h.drop_table('foo')
        self.assertEqual(h.tables(), set([]))
        h.close()

class TestIndices(TestDb):
    def test_create_if_exists(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.execute('create table pineapple (bar integer, baz integer);')
        dt.create_index(['bar', 'baz'], 'pineapple')

        with self.assertRaises(sqlalchemy.exc.OperationalError):
            dt.create_index(['bar', 'baz'], 'pineapple', if_not_exists = False)

    def test_create_if_not_exists(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.execute('create table mango (bar integer, baz integer);')
        dt.create_index(['bar', 'baz'], 'mango')

        # This should not raise an error.
        dt.create_index(['bar', 'baz'], 'mango', if_not_exists = True)

    def test_unique(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.execute('create table watermelon (bar integer, baz integer);')
        dt.create_index(['bar', 'baz'], 'watermelon', unique = True)
        observed = dt.execute('PRAGMA index_info(watermelon_bar_baz)')

        # Indexness
        self.assertIsNotNone(observed)

        # Indexed columns
        expected = [
          {u'seqno': 0, u'cid': 0, u'name': u'bar'},
          {u'seqno': 1, u'cid': 1, u'name': u'baz'},
        ]
        self.assertListEqual(observed, expected)

        # Uniqueness
        indices = dt.execute('PRAGMA index_list(watermelon)')
        for index in indices:
            if index[u'name'] == u'watermelon_bar_baz':
                break
        else:
            index = {}

        self.assertEqual(index[u'unique'], 1)

    def test_non_unique(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.execute('create table tomato (bar integer, baz integer);')
        dt.create_index(['bar', 'baz'], 'tomato')
        observed = dt.execute('PRAGMA index_info(tomato_bar_baz)')

        # Indexness
        self.assertIsNotNone(observed)

        # Indexed columns
        expected = [
          {u'seqno': 0, u'cid': 0, u'name': u'bar'},
          {u'seqno': 1, u'cid': 1, u'name': u'baz'},
        ]
        self.assertListEqual(observed, expected)

        # Uniqueness
        indices = dt.execute('PRAGMA index_list(tomato)')
        for index in indices:
            if index[u'name'] == u'tomato_bar_baz':
                break
        else:
            index = {}

        self.assertEqual(index[u'unique'], 0)

class SaveGetVar(TestDb):
    def savegetvar(self, var):
        h = DumpTruck(dbname = DB_FILE_MEMORY)
        h.save_var(u'weird', var)
        h.close()
        h = DumpTruck(dbname = DB_FILE_MEMORY)
        t=os.stat(DB_FILE_MEMORY).st_mtime
        self.assertEqual(h.get_var(u'weird'), var)
        h.close()
        assert os.stat(DB_FILE_MEMORY).st_mtime==t

class TestSaveVar(TestDb):
    def setUp(self):
        self.cleanUp()
        h = DumpTruck(dbname=DB_FILE_TMP)
        h.drop_table('_dumptruckvars')
        h.save_var(u'birthday', u'November 30, 1888')
        h.close()
        connection=sqlite3.connect(DB_FILE_TMP)
        self.cursor=connection.cursor()

    def test_insert(self):
        self.cursor.execute(u'SELECT key, value, type FROM `_dumptruckvars`')
        observed = self.cursor.fetchall()
        expected = [(u'birthday', u'November 30, 1888', u'text',)]
        self.assertEqual(observed, expected)

    def test_has_some_index(self):
        self.cursor.execute(u'PRAGMA index_list(_dumptruckvars)')
        indices = self.cursor.fetchall()
        self.assertNotEqual(indices,[])

class DumpTruckVars(TestDb):
    def save(self, key, value):
        h = DumpTruck(dbname=DB_FILE_TMP)
        h.drop_table('_dumptruckvars', if_exists=True)
        h.save_var(key, value)
        h.close()

    def check(self, key, value, sqltype):
        connection=sqlite3.connect(DB_FILE_TMP)
        self.cursor=connection.cursor()
        self.cursor.execute(u'SELECT key, value, `type` FROM `_dumptruckvars`')
        observed = self.cursor.fetchall()
        expected = [(key, buffer(str(value)), sqltype)]
        self.assertEqual(observed, expected)

    def get(self, key, value):
        h = DumpTruck(dbname = DB_FILE_TMP)
        self.assertEqual(h.get_var(key), value)
        h.close()

    def save_check_get(self, key, value, sqltype):
        self.save(key, value)
        self.check(key, value, sqltype)
        self.get(key, value)

class TestVarsSQL(DumpTruckVars):
    def test_integer(self):
        self.save_check_get(u'foo', 42, u'integer')

class TestSelect(TestDb):
    def test_select(self):
        shutil.copy(u'fixtures/landbank_branches.sqlite', u'.')
        h = DumpTruck(dbname = u'landbank_branches.sqlite')
        data_observed = h.execute(u'SELECT * FROM `branches` WHERE Fax is not null ORDER BY Fax LIMIT 3;')
        data_expected = [{'town': u'\r\nCenturion', 'date_scraped': 1327791915.618461, 'Fax': u' (012) 312 3647', 'Tel': u' (012) 686 0500', 'address_raw': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001\n (012) 686 0500\n (012) 312 3647', 'blockId': 14, 'street-address': None, 'postcode': u'\r\n0001', 'address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001', 'branchName': u'Head Office'}, {'town': u'\r\nCenturion', 'date_scraped': 1327792245.787187, 'Fax': u' (012) 312 3647', 'Tel': u' (012) 686 0500', 'address_raw': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001\n (012) 686 0500\n (012) 312 3647', 'blockId': 14, 'street-address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark', 'postcode': u'\r\n0001', 'address': u'\r\n420 Witch Hazel Ave\n\r\nEcopark\n\r\nCenturion\n\r\n0001', 'branchName': u'Head Office'}, {'town': u'\r\nMiddelburg', 'date_scraped': 1327791915.618461, 'Fax': u' (013) 282 6558', 'Tel': u' (013) 283 3500', 'address_raw': u'\r\n184 Jan van Riebeeck Street\n\r\nMiddelburg\n\r\n1050\n (013) 283 3500\n (013) 282 6558', 'blockId': 17, 'street-address': None, 'postcode': u'\r\n1050', 'address': u'\r\n184 Jan van Riebeeck Street\n\r\nMiddelburg\n\r\n1050', 'branchName': u'Middelburg'}]
        self.assertListEqual(data_observed, data_expected)
        os.remove('landbank_branches.sqlite')

class TestCreateTable(TestDb):
    def test_create_table(self):
        h = DumpTruck(dbname = DB_FILE_TMP)
        h.create_table({'foo': 0, 'bar': 1, 'baz': 2}, 'zombies')
        h.close()

        connection=sqlite3.connect(DB_FILE_TMP)
        cursor=connection.cursor()
        cursor.execute('SELECT foo, bar, baz FROM zombies')
        observed = cursor.fetchall()
        connection.close()

        expected = []
        self.assertListEqual(observed, expected)

    def test_if_not_exists(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.create_table({'foo': 'bar'}, 'baz')
        dt.create_table({'foo': 'bar'}, 'baz', error_if_exists = False)

    def test_if_exists(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.create_table({'foo': 'bar'}, 'zort')
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            dt.create_table({'foo': 'bar'}, 'zort', error_if_exists=True)

class TestCreateTableOnInsert(TestDb):
    def test_if_not_exists(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.create_table({'foo': 'bar'}, 'baz')
        dt.insert({'foo': 'bar'}, 'baz')
        dt.insert({'foo': 'bar'}, 'baz')

class SaveCheckSelect(TestDb):
    '''
    Save the value to the database,
    assert that it is stored as we expect,
    then retrieve it and assert that
    came out the same as it went in.
    '''

class SaveAndCheck(TestDb):
    def save_and_check(self, dataIn, tableIn, dataOut, tableOut = None, twice=False):
        if tableOut == None:
            tableOut = tableIn

        # Insert
        h = DumpTruck(dbname = DB_FILE_MEMORY)
        h.create_table(dataIn, tableIn)
        h.insert(dataIn, table_name=tableIn)
        if twice:
            h.insert(dataIn, table_name=tableIn)

        # Observe with DumpTruck
        observed = h.execute(u'SELECT * FROM "%s"' % tableOut)
        h.close()

        #Check
        expected = dataOut

        self.assertListEqual(observed, expected)

class SaveAndSelect(TestDb):
    def save_and_select(self, d):
        dt = DumpTruck()
        dt.create_table({'foo': d}, 'dumptruck')
        dt.insert({'foo': d})

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

class TestSaveBoolean(SaveAndCheck):
    def test_save_true(self):
        d = {'a': True}
        self.save_and_check(d, 'a', [OrderedDict(d)])

    def test_save_true(self):
        d = {'a': False}
        self.save_and_check(d, 'a', [OrderedDict(d)])

class TestSaveTwice(SaveAndCheck):
    def test_save_twice(self):
        d = {'modelNumber': 293}
        self.save_and_check(d, 'model-numbers', [OrderedDict(d), OrderedDict(d)], twice=True)

class TestSaveInt(SaveAndCheck):
    def test_save(self):
        d = {'modelNumber': 293}
        self.save_and_check(d, 'model-numbers', [OrderedDict(d)])

class TestSaveUnicodeKey(SaveAndCheck):
    def test_save(self):
        d = {u'英国': 'yes'}
        self.save_and_check(d, 'country', [OrderedDict(d)])

class TestSaveUnicodeEncodedKey(SaveAndCheck):
    def test_save(self):
        d = {u'英国': 'yes'}
        self.save_and_check(d, 'country', [OrderedDict(d)])

class TestSaveUnicodeEncodedTable(SaveAndCheck):
    def test_save(self):
        d = {'England': 'yes'}
        self.save_and_check(d, u'國家', [OrderedDict(d)])

class TestSaveArbitrarilyEncodedKey(SaveAndCheck):
    def test_save(self):
        d = {u'英国': 'yes'}
        self.save_and_check(d, 'country', [OrderedDict(d)])

# TODO: Figure out the bug here
#class TestSaveArbitrarilyEncodedTable(SaveAndCheck):
#    def test_save(self):
#        d = {'England': 'yes'}
#        self.save_and_check(d, '國家', [OrderedDict(d)])

class TestSaveWeirdTableName1(SaveAndCheck):
    def test_save(self):
        d = {'modelNumber': 293}
        self.save_and_check(d, 'This should-be a_valid.table+name!?', [OrderedDict(d)])

class TestSaveWeirdTableName2(SaveAndCheck):
    def test_save(self):
        d = {'lastname':'LeTourneau'}
        self.save_and_check(d, '`asoeu`', [OrderedDict(d)])

class TestSaveWeirdTableName3(SaveAndCheck):
    def test_save(self):
        d = {'lastname': 'LeTourneau'}
        self.save_and_check(d, '[asoeu]', [OrderedDict(d)])

class TestMultipleColumns(SaveAndSelect):
    def test_save(self):
        self.save_and_select({'firstname': 'Robert', 'lastname': 'LeTourneau'})

class TestSaveHyphen(SaveAndCheck):
    def test_save_int(self):
        self.save_and_check(
          {'model-number': 293}
        , 'model-numbers'
        , [OrderedDict({'model-number': 293})]
        )

class TestSaveString(SaveAndCheck):
    def test_save(self):
        self.save_and_check(
          {'lastname': 'LeTourneau'}
        , 'diesel-engineers'
        , [OrderedDict({'lastname': 'LeTourneau'})]
        )

class TestSaveDate(SaveAndCheck):
    def test_save(self):
        d = datetime.datetime.strptime('1990-03-30', '%Y-%m-%d').date()
        self.save_and_check(
          {'birthday': d}
        , 'birthdays'
        , [OrderedDict({u'birthday': u'1990-03-30'})]
        )

class TestSaveDateTime(SaveAndCheck):
    def test_save(self):
        d = datetime.datetime.strptime('1990-03-30', '%Y-%m-%d')
        self.save_and_check(
          {'birthday': d}
        , 'birthdays'
        , [OrderedDict({u'birthday': u'1990-03-30 00:00:00'})]
        )

class TestInvalidDumpTruckParams(TestDb):
    'Invalid parameters should raise appropriate errors.'

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
        self.assertFalse(os.path.isfile('/tmp/test_2.db'))
        h = DumpTruck(dbname=DB_FILE_MEMORY,auto_commit=False,vars_table='baz')
        self.assertTrue(os.path.isfile(DB_FILE_TMP))
#   self.assertEqual(h.auto_commit, False)
#   self.assertEqual(h.__vars_table, 'baz')

class TestParamsDefaults(TestDb):
    def test_params(self):
        self.assertFalse(os.path.isfile('dumptruck.db'))
        h = DumpTruck()
        self.assertTrue(os.path.isfile('dumptruck.db'))
#   self.assertEqual(h.auto_commit, True)
#   self.assertEqual(h.__vars_table, '_dumptruckvars')

class TestCaseInsensitivity(TestDb):
    "Insertions with two keys of the same case are not allowed."
    def test_bad_create_table(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            dt.create_table({'a': 'b', 'A': 'B'}, 'foo')

    def test_bad_insert(self):
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            dt.create_table({'a': 'b', 'A': 'B'}, 'foo')

class TestNull(SaveAndCheck):
    def test_create_table(self):
        "The first row must have a non-null value so the schema can be defined."
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        with self.assertRaises(ValueError):
            dt.create_table({'foo': None, 'bar': None}, 'one')
        dt.close()

    def test_first_insert(self):
        "The first row must have a non-null value so the schema can be defined."
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        with self.assertRaises(ValueError):
            dt.create_table({'foo': None, 'bar': None}, 'two')
        dt.close()

    def test_second_insert(self):
        "Inserting a second row that is all null adds an empty row."
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.create_table({'foo': 'uhtnh', 'bar': 'aoue'}, 'three')
        dt.insert({'foo': None, 'bar': None}, 'three')
        c = dt.execute('select count(*) as c from three')[0]['c']
        dt.close()
        self.assertEqual(c, 1)

    def test_empty_row_create_table(self):
        "The schema row must have a non-null value."
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        with self.assertRaises(ValueError):
            dt.create_table({}, 'two')
        dt.close()

    def test_empty_row_first_insert(self):
        "The first row must have a non-null value so the schema can be defined."
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        with self.assertRaises(ValueError):
            dt.create_table({}, 'two')
        dt.close()

    def test_empty_row_second_insert(self):
        "An empty row has no effect"
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.create_table({'foo': 'uhtnh', 'bar': 'aoue'}, 'nine')
        dt.insert({}, 'nine')
        c = dt.execute('select count(*) as c from nine')[0]['c']
        dt.close()
        self.assertEqual(c, 0)

    def test_no_rows_create_table(self):
        "The insert must have a row so the schema can be defined."
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        with self.assertRaises(ValueError):
            dt.create_table([], 'two')
        dt.close()

    def test_no_rows_first_insert(self):
        "Nothing happens if no rows are inserted to a table that isn't there."
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.insert([], 'ninety')
        self.assertSetEqual(dt.tables(), set())
        dt.close()

    def test_no_rows_second_insert(self):
        "Nothing happens if no rows are inserted to a table that is there."
        dt = DumpTruck(dbname = DB_FILE_MEMORY)
        dt.create_table({'foo': 'uhtnh', 'bar': 'aoue'}, 'ninety')
        dt.insert([], 'ninety')
        c = dt.execute('select count(*) as c from ninety')[0]['c']
        dt.close()
        self.assertEqual(c, 0)

if __name__ == '__main__':
    main()
