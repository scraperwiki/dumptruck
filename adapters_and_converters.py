import pickle
import json
import datetime

PICKLE_TYPES = [
]

def register_pickle(module):
    def adapt_pickle(val):
        return pickle.dumps(val)

    def convert_pickle(val):
        return pickle.loads(val)

    for t in PICKLE_TYPES:
        module.register_adapter(t, adapt_pickle)

    module.register_converter("pickle", convert_pickle)

def register_json(module):
    def adapt_json(val):
        return json.dumps(val)

    def adapt_jsonset(val):
        d = {k: None for k in val}
        return json.dumps(d)

    def convert_json(val):
        return json.loads(val)

    def convert_jsonset(val):
        return set(json.loads(val).keys())

    module.register_adapter(list, adapt_json)
    module.register_adapter(tuple, adapt_json)
    module.register_adapter(dict, adapt_json)
    module.register_adapter(set, adapt_jsonset)
    module.register_converter("json", convert_json)
    module.register_converter("jsonset", convert_jsonset)

def register_dates(module):
    def adapt_date(val):
        return val.isoformat()

    def adapt_datetime(val):
        return val.isoformat(" ")

    def convert_date(val):
        return datetime.date(*map(int, val.split("-")))

    def convert_datetime(val):
        datepart, timepart = val.split(" ")
        year, month, day = map(int, datepart.split("-"))
        timepart_full = timepart.split(".")
        hours, minutes, seconds = map(int, timepart_full[0].split(":"))
        if len(timepart_full) == 2:
            microseconds = int(timepart_full[1])
        else:
            microseconds = 0

        val = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds)
        return val


    module.register_adapter(datetime.date, adapt_date)
    module.register_adapter(datetime.datetime, adapt_datetime)
    module.register_converter("date", convert_date)
    module.register_converter("datetime", convert_datetime)

def register_adapters_and_converters(module):
    register_dates(module)
    register_json(module)
#   register_pickle(module)
