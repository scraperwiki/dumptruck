Hacks
----------
The default behavior for a particular database connection
is stored in the `Highwall.AUTO_COMMIT` attribute, so you
can change the default behavior by setting that to false.

    h.AUTO_COMMIT=False

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

### Views
Add some nice way of specifying views.

### Stored procedures.
Add some nice way of specifying stored procedures.
