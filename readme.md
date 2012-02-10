Highwall is an document-like interface to an SQLite database that lets you relax.
It supports the following database formats.

Quick start
---------
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

    h.save({"firstname":"Thomas","lastname":"Levine"},tablename="mine-engineers")

You can also pass a list of dictionaries.

    data=[
        {"firstname":"Thomas","lastname":"Levine"},
        {"firstname":"Julian","lastname":"Assange"}
    ]
    save(data)


* `indices=[]`: Columns to set as indices.

Slow start
---------
## Initialize

You can specify a few of keyword arguments when you initialize
the Highwall object. Here they are with their defaults.

* `dbname="highwall.db"`: File to use for the database

Generic functions
-----------
Highwall gives you eight functions.

These two are the coolest.

* `save`: Save to the database in a relaxing manner.
* `select`: Select from the database in a relaxing manner.

These two make it easy to save individual variables.

* `get_var`
* `save_var`

Here are some wrappers for common commands.

* `show_tables`
* `drop`: Delete a particular table.

These two let you run normal SQL.

* `execute`: Run raw SQL commands.
* `commit`: Commit SQL commands
