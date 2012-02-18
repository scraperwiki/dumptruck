Highwall
==============

Highwall is an document-like interface to an SQLite database that lets you relax.
It supports the following database formats.

Quick start
----------
Highwall helps you relax by making relational databases
feel more like document databases.

### Initialize

Open the database connection by initializing the a Highwall object

    h = Highwall()

### Saving
The simplest `save` call looks like this.

    h.save({"firstname":"Thomas","lastname":"Levine"},"diesel-engineers")

This saves a new row with "Thomas" in the "firstname" column and
"Levine" in the "lastname" column. It uses the table "diesel-engineers"
inside the database "highwall.db". It creates or alters the table
if it needs to.

### Retrieving
Once the database contains data, you can retrieve it.

    data=h.exec('SELECT * FROM `diesel-engineers`')

The data come out as a list of dictionaries, with one dictionary per row.

### Individual values
It's often useful to be able to quickly and easily save one metadata value.
For example, to record which page the last run of a script managed to get up to. 

    h.save_var('last_page', 27)
    27 == h.get_var('last_page')

It's stored in a table that you can specify when initializing Highwall.
If you don't specify one, it's stored in `_highwallvars`.

If you want to save anything other than an int, float or string type,
use json or pickle.

Slow start
-------
### Initialize

You can specify a few of keyword arguments when you initialize the Highwall object.
For example, if you want the database file to be `bucket=wheel-excavators.db`,
you can use this.

    h = Highwall(dbname="bucket-wheel-excavators.db")

### Saving
As discussed earlier, the simplest `save` call looks like this.

    h.save({"firstname":"Thomas","lastname":"Levine"})

But you can also pass a list of dictionaries.

    data=[
        {"firstname":"Thomas","lastname":"Levine"},
        {"firstname":"Julian","lastname":"Assange"}
    ]
    h.save(data)

You can even past nested structures; dictionaries,
sets and lists will automatically be dumped to JSON.

    data=[
        {"title":"The Elements of Typographic Style","authors":["Robert Bringhurst"]},
        {"title":"How to Read a Book","authors":["Mortimer Adler","Charles Van Doren"]}
    ]
    h.save(data)

It would be cool if I can come up with a way for `h.save` to return
the [rowid](http://www.sqlite.org/lang_createtable.html#rowid)(s) of the
row(s) that are being saved. Dunno how annoying this would be....

### Indices
Highwall allows you to manage indices as if they were
normal Python objects

#### Creating
First, create an index object, specifying the columns.

    i1=Index('modelNumber')

Then add it to the set of indices for the table.

    h.indices['models'].add(i1)

If you want a unique index, do this.

    i2=Index('year',unique=True)
    h.indices['models'].add(i2)

If you specify a column that already contains non-distinct values, you will receive an error.

You can specify multiple single-column indices by passing a list of column names.

    h.indices['machines']=Index(['modelNumber','serialNumber'])

#### Retrieving
You can display the indices for a database like so.

    print(h.indices)

You can retrieve them as a dictionary and save them somewhere else.

    d=h.indices

In particular, you might want to copy indices from one table to another.

    s=h.indices['models']
    h.indices['models-test']=s

Indices on one table act like a set, so this is how you drop an index:

    h.indices['models'].remove(Index('modelnumber'))

Reference
-----------------
### Initializing
Highwall's initialization method takes the following keyword arguments.

    Highwall(dbname='highwall.db',auto_commit=True,vars_table="_highwallvars")

* `dbname` is the database file to save to; the default is highwall.db.
* `vars_table` is the name of the table to use for `Highwall.get_var`
and `Highwall.save_var`; default is `_highwallvars`. Set it to `None`
to disable the get_var and save_var methods.
* `auto_commit` is whether changes to the database should be automatically committed;
if it is set to `False`, changes must be committed with the `commit` method
or with the `commit` keywoard argument.

### Summary of methods

Basic functions, around which the others are based.

* `save`: Save to the database in a relaxing manner.
* `execute`: Run raw SQL commands. Results are returned in a relaxing data structure.

These two make it easy to save individual variables.

* `get_var`: Save one variable to the database in a relaxing manner.
* `save_var`: Retrieve one variable from the database in a relaxing manner.

These two are wrappers for common SQL commands.

* `show_tables`: Return a set containing the names of the tables in the database.
* `drop`: Delete a particular table.

This one lets you commit any changes that you previously delayed.

* `commit`: Manually commit changes to the database.

### Standard options to the methods
By default, the `save`, `get_var`, `drop` and `execute`
methods automatically commit changes.
You can stop one of them from committing by passing
`commit=False` to it. For example:

    h=Highwall()
    h.save({"name":"Bagger 293","manufacturer":"TAKRAF","height":95},commit=False)
