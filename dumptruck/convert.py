#!/usr/bin/env python2
'Convert a dictionary into a form ready to be inserted.'

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

from copy import copy
import re
import datetime

QUOTEPAIRS = [
  (u'`', u'`'),
  (u'[', u']'),
]

def convert(data):
  # Allow single rows to be dictionaries.
  try:
    data.items
  except AttributeError:
    # It is a dictionary
    pass
  else:
    # It is not a dictionary
    data = [data]

  # http://stackoverflow.com/questions/1952464/
  # in-python-how-do-i-determine-if-a-variable-is-iterable
  try:
    [e for e in data]
  except TypeError:
    raise TypeError(
      'The data argument must be a mapping (like a dict) '
      'or an iterable of mappings.'
    )

  for row in data:
    for key, value in row.items():
      if value == None:
        del(data[key])

    checkdata(row)

  data_quoted = [{quote(k): v for k, v in row.items()} for row in data]
  return data_quoted

def simplify(text):
  return re.sub(r'[^a-zA-Z0-9]', '', text)

def quote(text):
  'Handle quote characters'

  # Convert to unicode.
  if type(text) != unicode:
    text = text.decode('utf-8')

  # Look for quote characters. Keep the text as is if it's already quoted.
  for qp in QUOTEPAIRS:
    if text[0] == qp[0] and text[-1] == qp[-1] and len(text) >= 2:
      return text

  # If it's not quoted, try quoting
  for qp in QUOTEPAIRS:
    if qp[1] not in text:
      return qp[0] + text + qp[1]

  #Darn
  raise ValueError(u'The value "%s" is not quoted and contains too many quote characters to quote' % text)

def checkdata(data):
  for key, value in data.items():
    # Column names
    if key in [None, '']:
      raise ValueError('key must not be blank')
    elif type(key) not in (unicode, str):
      raise ValueError(u'The column name must be of unicode or str type. The column name ("%s") is of type %s. If this error doesn\'t make sense, try "unicode(\'%s\')".' % (key, type(key), key))
