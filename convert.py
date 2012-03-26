"Convert a dictionary into a form ready to be inserted."
from copy import copy
import re
import datetime

def convert(datarow_raw):
  data = copy(datarow_raw)
  data = __remove_null(data)
  data = __checkdata(data)
  data = __jsonify(data)
  data = __convdata(data)

  data_quoted = {quote(k): v for k, v in data.items()}
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

def __convdata(data):
  #Based on scraperlibs
  jdata = {}
  for key, value in data.items():
    if type(value) == datetime.date:
      value = value.isoformat()
    elif type(value) == datetime.datetime:
      if value.tzinfo is None:
        value = value.isoformat()
      else:
        value = value.astimezone(pytz.timezone('UTC')).isoformat()
        assert "+00:00" in value
        value = value.replace("+00:00", "")
    elif value == None:
      pass
    elif type(value) == str:
      try:
        value = value.decode("utf-8")
      except:
        raise UnicodeEncodeError("Binary strings must be utf-8 encoded")
    elif type(value) not in [int, bool, float, unicode, str]:
      value = unicode(value)
    jdata[key] = value
  data = jdata
  return data
