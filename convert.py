"Convert a dictionary into a form ready to be inserted."

def convert(datarow_raw):
  data = copy(datarow_raw)
  data = __remove_null(data)
  data = __checkdata(data)
  data = __jsonify(data)
  data = __convdata(data)
  return data

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

def __checkdata(data):
  #Based on scraperlibs
  for key in data.keys():
    if not key:
      raise ValueError('key must not be blank')
    elif type(key) not in (unicode, str):
      raise ValueError('key must be string type')
    elif not re.match("[a-zA-Z0-9_\- ]+$", key):
      raise ValueError('key must be simple text')
    elif key[0] == '[' and key[-1] == ']':
      #Remove the brackets so we can add them back later.
      data[key[1:-1]] = data[key]
      del(data[key])
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
