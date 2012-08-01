#!/usr/bin/env python2

# Copyright 2012 Thomas Levine

# This file is part of DumpTruck.

# DumpTruck is free software: you can redistribute it and/or modify
# it under the terms of the GNU Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# DumpTruck is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Public License for more details.

# You should have received a copy of the GNU Public License
# along with DumpTruck.  If not, see <http://www.gnu.org/licenses/>.

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
