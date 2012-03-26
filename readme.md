Highwall
==============

Highwall is an document-like interface to an SQLite database that lets you relax.
It supports the following database formats.

Quick start
----------
Highwall helps you relax by making relational databases
feel more like document databases.

### Install

    # This doesn't actually work yet; this here so I don't forget
    # to put it in once I put it on PyPI once it's ready.
    pip install highwall

### Initialize

Open the database connection by initializing the a Highwall object

    h = Highwall()

### Save
The simplest `insert` call looks like this.

    h.insert({"firstname":"Thomas","lastname":"Levine"},"diesel-engineers")

This saves a new row with "Thomas" in the "firstname" column and
"Levine" in the "lastname" column. It uses the table "diesel-engineers"
inside the database "highwall.db". It creates or alters the table
if it needs to.

### Retrieve
Once the database contains data, you can retrieve them.

    data=h.execute('SELECT * FROM `diesel-engineers`')

The data come out as a list of dictionaries, with one dictionary per row.


Slow start
-------
### Initialize

You can specify a few of keyword arguments when you initialize the Highwall object.
For example, if you want the database file to be `bucket=wheel-excavators.db`,
you can use this.

    h = Highwall(dbname="bucket-wheel-excavators.db")

It actually takes up to three keyword arguments.

    Highwall(dbname='highwall.db',auto_commit=True,vars_table="_highwallvars")

* `dbname` is the database file to save to; the default is highwall.db.
* `vars_table` is the name of the table to use for `Highwall.get_var`
and `Highwall.save_var`; default is `_highwallvars`. Set it to `None`
to disable the get_var and save_var methods.
* `auto_commit` is whether changes to the database should be automatically committed;
if it is set to `False`, changes must be committed with the `commit` method
or with the `commit` keywoard argument.

### Saving
As discussed earlier, the simplest `insert` call looks like this.

    h.insert({"firstname":"Thomas","lastname":"Levine"})

But you can also pass a list of dictionaries.

    data=[
        {"firstname":"Thomas","lastname":"Levine"},
        {"firstname":"Julian","lastname":"Assange"}
    ]
    h.insert(data)

You can even past nested structures; dictionaries,
sets and lists will automatically be dumped to JSON.

    data=[
        {"title":"The Elements of Typographic Style","authors":["Robert Bringhurst"]},
        {"title":"How to Read a Book","authors":["Mortimer Adler","Charles Van Doren"]}
    ]
    h.insert(data)

Column names and table names automatically get quoted if you pass them without quotes,
so you can use bizarre table and column names, like `no^[hs!'e]?'sf_"&'`

It would be cool if I can come up with a way for `h.insert` to return
the [rowid](http://www.sqlite.org/lang_createtable.html#rowid)(s) of the
row(s) that are being saved. Dunno how annoying this would be....

### Individual values
It's often useful to be able to quickly and easily save one metadata value.
For example, you can record which page the last run of a script managed to get up to.

    h.save_var('last_page', 27)
    27 == h.get_var('last_page')

It's stored in a table that you can specify when initializing Highwall.
If you don't specify one, it's stored in `_highwallvars`.

If you want to save anything other than an int, float or string type,
use json or pickle.

### Helpers
Highwall provides specialized wrapper around some common commands.

`Highwall.tables` returns a set of all of the tables in the database.

    h.tables()

`Highwall.drop` drops a table.

    h.drop("diesel-engineers")

### Creating empty tables
When working with relational databases, one typically defines a schema
before populating the database. You can use the `Highwall.insert` method
like this by calling it with `create_only = True`.

For example, if the table `tools` does not exist, the following call will create the table
`tools` with the columns `toolName` and `weight`, with the types `TEXT` and `INTEGER`,
respectively, but will not insert the dictionary values ("jackhammer" and 58) into the table.

    h.create_table({"toolName":"jackhammer", "weight": 58}, "tools")

### Indices

#### Creating
Highwall contains a special method for creating indices. To create an index,
first create an empty table. (See "Creating empty tables" above.)
Then, use the `Highwall.add_index` method.

    h.create_index('tools', ['toolName'])

This will create a non-unique index on the column `tool`. To create a unique
index, use the keyword argument `unique = True`.

    h.create_index('tools', ['toolName'], unique = True)

You can also specify multi-column indices.

    h.create_index('tools', ['toolName', 'weight'])

Highwall names these indices according to the names of the relevant table and columns.
The index created in the previous example might be named `tools_toolName_weight0`.
The 0 is an arbitrary number that is changed in case the index name would otherwise
be the same as the name of an existing index.

#### Other index manipulation
Highwall does not implement special methods for viewing or removing indices, but here
are the relevant SQLite SQL commands.

The following command lists indices on the `tools` table.

    h.execute('PRAGMA index_list(tools)')

The following command gives more information about the index named `tools_toolName_weight0`.

    h.execute('PRAGMA index_list(tools_toolName_weight0)')

And this one deletes the index.

    h.execute('DROP INDEX tools_toolName_weight0')

For more information on indices and, particularly, the `PRAGMA` commands, check
the [SQLite documentation]().

### Delaying commits
By default, the `insert`, `get_var`, `drop` and `execute` methods automatically commit changes.
You can stop one of them from committing by passing `commit=False` to the method.
Commit manually with the `commit` method.  For example:

    h=Highwall()
    h.insert({"name":"Bagger 293","manufacturer":"TAKRAF","height":95}, commit=False)
    h.save_var('page_number', 42, commit=False)
    h.commit()

When you use `Highwall.index_info` or `Highwall.index_list`,
your changes are automatically committed. If you need to delay the commits,
you can use the underlying getter method, passing a `commit = True` keyword argument.
