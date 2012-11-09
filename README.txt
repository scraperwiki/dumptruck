DumpTruck
==============
DumpTruck is a document-like interface to a SQLite database.

Quick start
----------
Install, save data and retrieve it using default settings.

### Install

    pip2 install dumptruck || pip install dumptruck

### Initialize

Open the database connection by initializing the a DumpTruck object

    dt = DumpTruck()

### Save
The simplest `insert` call looks like this.

    dt.insert({"firstname":"Thomas","lastname":"Levine"})

This saves a new row with "Thomas" in the "firstname" column and
"Levine" in the "lastname" column. It uses the table "dumptruck"
inside the database "dumptruck.db". It creates or alters the table
if it needs to.

If you insert one row, `DumpTruck.insert` returns the rowid of the row.

    dt.insert({"foo", "bar"}, "new-table") == 1

If you insert many rows, `DumpTruck.insert` returns a list of the rowids of the
new rows.

    dt.insert([{"foo", "one"}, {"foo", "two"}], "new-table") == [2, 3]

By default, insert doesn't automatically replace rows which have the key: you
can use `dt.upsert` (with the same syntax) instead to change this behaviour.

### Retrieve
Once the database contains data, you can retrieve them.

    data = dt.dump()

The data come out as a list of ordered dictionaries,
with one dictionary per row.

Slow start
-------
### Initialize

You can specify a few of keyword arguments when you initialize the DumpTruck object.
For example, if you want the database file to be `bucket-wheel-excavators.db`,
you can use this.

    dt = DumpTruck(dbname="bucket-wheel-excavators.db")

It actually takes up to four keyword arguments.

    DumpTruck(dbname='dumptruck.db', auto_commit = True, vars_table = "_dumptruckvars", adapt_and_convert = True)

* `dbname` is the database file to save to; the default is dumptruck.db.
* `vars_table` is the name of the table to use for `DumpTruck.get_var`
    and `DumpTruck.save_var`; default is `_dumptruckvars`. Set it to `None`
    to disable the get_var and save_var methods.
* `auto_commit` is whether changes to the database should be automatically committed;
    if it is set to `False`, changes must be committed with the `commit` method
    or with the `commit` keywoard argument.
* `adapt_and_convert` is whether types should be converted automatically; with
    this on dates get inserted as dates, lists as lists, &c.

### Saving
As discussed earlier, the simplest `insert` call looks like this.

    dt.insert({"firstname": "Thomas", "lastname": "Levine"})

#### Different tables
By default, that saves to the table `dumptruck`. You can specify different table;
this saves to the table `diesel-engineers`.

    dt.insert({"firstname": "Thomas", "lastname": "Levine"}, "diesel-engineers")

#### Multiple rows
You can also pass a list of dictionaries.

    data=[
        {"firstname": "Thomas", "lastname": "Levine"},
        {"firstname": "Julian", "lastname": "Assange"}
    ]
    dt.insert(data)

#### Complex objects
You can even past nested structures; dictionaries,
sets and lists will automatically be dumped to JSON.

    data=[
        {"title":"The Elements of Typographic Style","authors":["Robert Bringhurst"]},
        {"title":"How to Read a Book","authors":["Mortimer Adler","Charles Van Doren"]}
    ]
    dt.insert(data)

Your data will be stored as JSON. When you query it, it will
come back as the original Python objects.

And if you have some crazy object that can't be JSONified,
you can use the dead-simple pickle interface.

    # This fails
    data = {"weirdthing": {range(100): None}
    dt.insert(data)

    # This works
    from DumpTruck import Pickle
    data = Pickle({"weirdthing": {range(100): None})
    dt.insert(data)

It automatically pickles and unpickles your complex object for you.

#### Names
Column names and table names automatically get quoted if you pass them without quotes,
so you can use bizarre table and column names, like `no^[hs!'e]?'sf_"&'`

#### Null values
`None` dictionary values are always equivalent to non-existance of the key.
That is, these insert commands are equivalent.

    dt = DumpTruck()
    dt.insert({ u'foo': 8, u'bar': None})
    dt.insert({ u'foo': 8})

Passing an empty dictionary creates a new row with all NULL values.

    # These all create a row with all NULL values.
    dt.insert({})
    dt.insert([{}])
    dt.insert({u'potato': None})

More precisely, they set the values to the default values via this SQL.

    INSERT INTO foo DEFAULT VALUES

Passing an empty list to `insert` inserts zero rows (rather than one);
this command does nothing.

    dt.insert([])

You can pass zero rows or empty rows to `DumpTruck.insert`, but you'll get an
error if you try passing them to `DumpTruck.create_table`.

### Retrieving

You can use normal SQL to retrieve data from the database.

    data = dt.execute('SELECT * FROM `diesel-engineers`')

The data come back as a list of dictionaries, one dictionary
per row. They are coerced to different python types depending
on their database types.

### Individual values
It's often useful to be able to quickly and easily save one metadata value.
For example, you can record which page the last run of a script managed to get up to.

    dt.save_var('last_page', 27)
    27 == dt.get_var('last_page')

It's stored in a table that you can specify when initializing DumpTruck.
If you don't specify one, it's stored in `_dumptruckvars`.

If you want to save anything other than an int, float or string type,
use json or pickle.

### Helpers
DumpTruck provides specialized wrapper around some common commands.

`DumpTruck.tables` returns a set of all of the tables in the database.

    dt.tables()

`DumpTruck.drop` drops a table.

    dt.drop("diesel-engineers")

`DumpTruck.dump` returns the entire particular table as a list of dictionaries.

    dt.dump("coal")

It's equivalent to running this:

    dt.execute('SELECT * from `coal`;')

### Creating empty tables
When working with relational databases, one typically defines a schema
before populating the database. You can use the `DumpTruck.insert` method
like this by calling it with `create_only = True`.

For example, if the table `tools` does not exist, the following call will create the table
`tools` with the columns `toolName` and `weight`, with the types `TEXT` and `INTEGER`,
respectively, but will not insert the dictionary values ("jackhammer" and 58) into the table.

    dt.create_table({"toolName":"jackhammer", "weight": 58}, "tools")

If you are concerned about the order of the tables, pass an OrderedDict.

    dt.create_table(OrderedDict([("toolName", "jackhammer"), ("weight", 58)]), "tools")

The columns will be created in the specified order.

### Indices

#### Creating
DumpTruck contains a special method for creating indices. To create an index,
first create an empty table. (See "Creating empty tables" above.)
Then, use the `DumpTruck.create_index` method.

    dt.create_index(['toolName'], 'tools')

This will create a non-unique index on the column `tool`. To create a unique
index, use the keyword argument `unique = True`.

    dt.create_index(['toolName'], 'tools', unique = True)

You can also specify multi-column indices.

    dt.create_index(['toolName', 'weight'], 'tools')

DumpTruck names these indices according to the names of the relevant table and columns.
The index created in the previous example might be named `dt__tools_toolName_weight`.

#### Other index manipulation
DumpTruck does not implement special methods for viewing or removing indices, but here
are the relevant SQLite SQL commands.

The following command lists indices on the `tools` table.

    dt.execute('PRAGMA index_list(tools)')

The following command gives more information about the index named `dt__tools_toolName_weight`.

    dt.execute('PRAGMA index_info(dt__tools_toolName_weight)')

And this one deletes the index.

    dt.execute('DROP INDEX dt__tools_toolName_weight')

For more information on indices and, particularly, the `PRAGMA` commands, check
the [SQLite documentation]().

### Delaying commits
By default, the `insert`, `get_var`, `drop` and `execute` methods automatically commit changes.
You can stop one of them from committing by passing `commit=False` to the method.
Commit manually with the `commit` method.  For example:

    dt = DumpTruck()
    dt.insert({"name":"Bagger 293","manufacturer":"TAKRAF","height":95}, commit=False)
    dt.save_var('page_number', 42, commit=False)
    dt.commit()
