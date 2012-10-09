#!/usr/bin/env python2
# This file is part of DumpTruck.

# Copyright (C) 2012 ScraperWiki Ltd. and other contributors
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.


class IndexList:
  'Like running `PRAGMA index_list(?);`'
  def __init__(self,highwall_object):
    self.h = highwall_object

  def __getitem__(self, table_name):
    "Retrive the indices for a table."
    return IndexInfo(self.h, table_name)

  def __setitem__(self, index_info):
    "I don't think this will ever be implemented."
    print "This should not run."

class IndexInfo:
  'Like running `PRAGMA index_info(?);`'

  class IndexNameError(Exception):
    pass

  def __init__(self,highwall_object, table_name):
    self.h = highwall_object
    self.table_name = table_name
    self.table_indices = self.h.execute("PRAGMA index_list(`%s`)" % table_name, commit = False)

  def __getitem__(self, index_name):
    "Retrive an index."
    index = self.h.execute("PRAGMA index_info(`%s`)" % index_name, commit = False)

    # Determine whether it's unique.
    for i in self.table_indices:
      if i['name'] == index_name:
        unique = i['unique']
        break

    try:
      unique
    except NameError:
      raise self.IndexNameError('There is no index with the name "%s".' % index_name)

    return Index([col['name'] for col in index], unique = unique)

  def __setitem__(self, index_name, index):
    # This is currently a bit vulnerable to injection.
    sql = "CREATE %s INDEX IF NOT EXISTS `%s` ON `%s` (%s)"
    indexed_columns = ','.join(index.columns)
    str_unique = 'UNIQUE' if index.unique else ''
    self.h.execute(sql % (str_unique, index_name, self.table_name, indexed_columns))

class Index:
  "An index absent of a table"

  #COLNAME_TYPES = set([unicode, str, int, IndexedColumn])
  COLNAME_TYPES = set([unicode, str, int])

  class DuplicateColumnError(Exception):
    pass

  def __init__(self, columns, unique = False):
    self.unique = unique

    # Set columns
    if type(columns) in self.COLNAME_TYPES:
      # One column
      self.columns = [str(columns)]
    elif set(map(type, columns)).issubset(self.COLNAME_TYPES):
      # Multiple columns
      str_columns = map(str, columns)
      if len(set(str_columns)) != len(columns):
        raise self.DuplicateColumnError
      else:
        self.columns = str_columns

class IndexedColumn:
  "This is how you do COLLATE or ASC."

  def __init__(self, collate = None, sort = None):
    self.collate = collate
    self.sort = sort
    raise NotImplementedError("IndexedColumn doesn't work yet.")
