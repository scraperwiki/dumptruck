#!/usr/bin/env python2
'Convert a dictionary into a form ready to be inserted.'

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

from copy import copy
import re
import datetime
from collections import OrderedDict

QUOTEPAIRS = [
  (u'`', u'`'),
  (u'[', u']'),
]

def convert(data):

  try:
    data.keys
  except AttributeError:
    # http://stackoverflow.com/questions/1952464/
    # in-python-how-do-i-determine-if-a-variable-is-iterable
    try:
      [e for e in data]
    except TypeError:
      raise TypeError(
        'The data argument must be a mapping (like a dict), '
        'an iterable of pairs or an iterable either of those.'
      )
  else:
    # It is a single dictionary
    data = [data]

  data_quoted = []
  for row in data:

    checkdata(row)

    # Delete nones
    for key, value in row.items():
      if value == None:
        del(row[key])

    if len(set([k.lower() for k in row.keys()])) != len(row.keys()):
      raise ValueError(u'You passed the same column name twice. (Column names are insensitive to case.)')

    data_quoted.append(zip([quote(k) for k in row.keys()], row.values()))
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
    elif type(value) == dict and not set(map(type, value.keys())).issubset({unicode, str}):
      raise ValueError('Dictionary keys must all be str or unicode for database insert.')
