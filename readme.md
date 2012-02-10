Highwall is an document-like interface to relational databases that lets you relax.
It supports the following database formats.

* SQLite
* Comma separated values

How to
-----------
Highwall gives you five generic functions.

These two are the coolest.

* `save`
* `select`

These two make it easy to save individual variables.

* `get_var`
* `save_var`

This shows you the tables you have.

* `show_tables`

Format-specific functions
--------------
For the SQLite database format, the following additional functions are allowed.

* `execute`: Run raw SQL commands.
* `commit`: Commit SQL commands

For the CSV database format, the following additional functions are allowed.

* `drop`: Delete a particular table.
