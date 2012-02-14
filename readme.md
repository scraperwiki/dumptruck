Highwall is an document-like interface to an SQLite database that lets you relax.
It supports the following database formats.

Quick start
==========

Highwall makes relational databases feel more like document databases.

## Initialize

Open the database connection by initializing the a Highwall object

    h = Highwall()

## Saving
The simplest `save` call looks like this.

    h.save({"firstname":"Thomas","lastname":"Levine"})

This saves a new row with "Thomas" in the "firstname" column and
"Levine" in the "lastname" column. It uses the table "default"
inside the database "highwall.db". It creates or alters the table
if it needs to.

You can specify the table with the `tablename` parameter.

    h.save({"firstname":"Thomas","lastname":"Levine"},tablename="diesel-engineers")


Slow start
=======
## Initialize

You can specify a few of keyword arguments when you initialize
the Highwall object. Here they are with their defaults.

* `dbname="highwall.db"`: File to use for the database

So you if you want the database file to be `bucket-wheel-excavators.db`,
you can use this.

    h = Highwall(dbname="bucket-wheel-excavators.db")

## Saving
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

## Indices
You can specify indices for the the database tables.

    h.indices('models',['modelNumber'])

You can specify multiple single-column indices by passing a list of column names.

    h.indices('machines',[['modelNumber','serialNumber']])

If you specify a column that contains non-distinct values, you will receive an error.
You can override this with `force=True` to arbitrarily delete all but one of them.

    h.indices('models',['modelNumber'],force=True)

Reference
=================
## Summary of methods
Highwall gives you eight functions.

These two are the coolest.

* `save`: Save to the database in a relaxing manner.
* `load`: Select from the database in a relaxing manner.

These two make it easy to save individual variables.

* `get_var`
* `save_var`

Here are some wrappers for common commands.

* `show_tables`
* `drop`: Delete a particular table.

These two let you run normal SQL to interface directly with pysqlite.

* `execute`: Run raw SQL commands.
* `commit`: Commit SQL commands

## Methods
### save
### load
### get_var
### save_var
### show_tables
### drop
### execute
### commit

## Options to the methods
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
