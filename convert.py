"Convert a dictionary into a form ready to be inserted."
from copy import copy
import re
import datetime
from json import loads, dumps

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

  data = [__jsonify(__checkdata(__remove_null(row))) for row in data]

  data_quoted = [{quote(k): v for k, v in row.items()} for row in data]
  return data_quoted

def __remove_null(data):
  for key, value in data.items():
    if value == None:
      del(data[key])
  return data

def __jsonify(data):
  for key, value in data.items():
    if type(value)==set:
      # Convert sets to dicts
      data[key] = dict(zip( list(value), [None]*len(value) ))

    if type(value) in (list, dict):
      try:
        value = dumps(value)
      except TypeError:
        raise TypeError("The value for %s is a complex object that could not be dumped to JSON.")
  return data


QUOTEPAIRS = [
  ('[', ']'),
# ('"', '"'),
# ('\'', '\''),
  ('`', '`'),
]
#QUOTECHARS = '\'"`'
QUOTECHARS = '`'
def quote(text):
  "Handle quote characters"
  # Look for quote characters. Keep the text as is if it's already quoted.
  for qp in QUOTEPAIRS:
    if text[0] == qp[0] and text[-1] == qp[-1] and len(text) >= 2:
      return text

  # If it's not quoted, try quoting
  for qc in QUOTECHARS:
    if qc not in text:
      return qc + text + qc

  #If the text has the quote characters, check for brackets.
  if ']' not in text:
    return '[' + text + ']'

  #Darn
  raise ValueError('The value "%s" is not quoted and contains too many quote characters to quote' % text)

def __checkdata(data):
  #Based on scraperlibs
  for key in data.keys():
    if key in [None, '']:
      raise ValueError('key must not be blank')
    elif type(key) not in (unicode, str):
      raise ValueError('key must be string type')
#   elif not re.match("[a-zA-Z0-9_\- ]+$", key):
#     raise ValueError('key must be simple text')
  return data
