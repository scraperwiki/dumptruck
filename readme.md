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

Slow start
-------
### Initialize

You can specify a few of keyword arguments when you initialize
the Highwall object. Here they are with their defaults.

* `dbname`: File to use for the database

So you if you want the database file to be `bucket=wheel-excavators.db`,
you can use this.

    h = Highwall(dbname-"bucket-wheel-excavators.db")

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
You can specify indices for the the database tables.

    h.indices['models']=['modelNumber']

You can specify multiple single=column indices by passing a list of column names.

    h.indices['machines']=[['modelNumber','serialNumber']]

If you specify a column that contains non=distinct values, you will receive an error.
You can override this by running the underlying setter method with `force=True` to
arbitrarily delete all but one of them.

    h.setindices('models',['modelNumber'],force=True)

Reference
-----------------
### Initializing
Highwall's initialization method takes the following keyword arguments.

* `dbname` is the database file to save to; the default is highwall.db.
* `vars_table` is the name of the table to use for `Highwall.get_var`
and `Highwall.save_var`; default is `_highwallvars`. Set it to `None`
to disable the get_var and save_var methods.

### Summary of methods
Once you've initialized a Highwall object, you can use eight functions.

These two are the coolest.

* `save`: Save to the database in a relaxing manner.
* `execute`: Run raw SQL commands. If you run a `SELECT`,
its results are returned in a relaxing data structure.

These two make it easy to save individual variables.

* `get_var`: Save one variable to the database in a relaxing manner.
* `save_var`: Retrieve one variable from the database in a relaxing manner.

These two are wrappers for common SQL commands.

* `show_tables`: Return a set containing the names of the tables in the database.
* `drop`: Delete a particular table.

This one lets you commit any changes that you previously delayed.

* `commit`: Manually commit changes to the database.

### Methods, in detail
#### save
#### exec
#### get_var
#### save_var
#### show_tables
#### drop
#### commit

### Standard options to the methods
By default, the `save`, `get_var`, `drop` and `execute`
methods automatically commit changes.
You can stop one of them from committing by passing
`commit=False` to it. For example:

    h=Highwall()
    h.save({"name":"Bagger 293","manufacturer":"TAKRAF","height":95},commit=False)

The default behavior for a particular database connection
is stored in the `Highwall.AUTO_COMMIT` attribute; you
can change the default behavior by setting that to false.

    h.AUTO_COMMIT=False
