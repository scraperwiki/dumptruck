"Convert a dictionary into a form ready to be inserted."
from copy import copy
import re
import datetime
from json import loads, dumps

QUOTEPAIRS = [
  ('`', '`'),
  ('[', ']'),
]

def convert(data):
  # Allow single rows to be dictionaries.
  if type(data)==dict:
    data = [data]

  # http://stackoverflow.com/questions/1952464/
  # in-python-how-do-i-determine-if-a-variable-is-iterable
  try:
    set([ type(e) for e in data])==set([dict])
  except TypeError:
    raise TypeError('The data argument must be a dict or an iterable of dicts.')

  data = [checkdata(row) for row in data]
  data_quoted = [{quote(k): v for k, v in row.items()} for row in data]
  return data_quoted


def quote(text):
  "Handle quote characters"
  # Look for quote characters. Keep the text as is if it's already quoted.
  for qp in QUOTEPAIRS:
    if text[0] == qp[0] and text[-1] == qp[-1] and len(text) >= 2:
      return text

  # If it's not quoted, try quoting
  for qp in QUOTEPAIRS:
    if qp[1] not in text:
      return qp[0] + text + qp[1]

  #Darn
  raise ValueError('The value "%s" is not quoted and contains too many quote characters to quote' % text)

def checkdata(data):
  for key, value in data.items():
    if value == None:
      del(data[key])

    # Column names
    elif key in [None, '']:
      raise ValueError('key must not be blank')
    elif type(key) not in (unicode, str):
      raise ValueError('key must be string type')

    # JSON
    elif type(value) == dict:
      assert_text(value.keys())
    elif type(value) in [list, set]:
      assert_text(value)

  return data

def assert_text(vals):
  if not set(map(type, vals)).issubset(set([str, unicode])):
    raise TypeError("Non-text keys cannot be JSONified.")
