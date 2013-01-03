Future
------------

`DumpTruck.execute` can return a generator or a list; previously, it only
returned a list.

`DumpTruck.{get,save}_var` uses less of a hack for the table that it creates and deletes.

Make `Pickle` work properly.

Allow very long numbers to be inserted.

`DumpTruck.create_index` adds a `NOT NULL` constraint on the column if a unique
index is created.

Added `DumpTruck.rollback` for rolling back transactions


Change how dumptruck variables work. This may cause incompatibilties
with databases created with an older version of dumptruck.

Version 0.1.1 (January 2013)
----
Allow dumptruck to be install on a system that does not already have lxml.

Version 0.1.0 (November 2012)
----
Handles lxml strings correctly.

Version 0.0.9 (November 2012)
----
Set author correctly.

Version 0.0.8 (November 2012)
----
Add upsert command (Dragon).

Version 0.0.7 (October 2012)
----
A connection can now be made without the adapters and converters by setting the
`adapt_and_convert` flag.

But this `adapt_and_convert` thing is sort of broken; if you open multiple
dumptruck instances within the same session, the first setting will be used.
This is because the setting is made on the `sqlite3` module, which is cached,
and we haven't figured out how to ignore the cache.

We also switched to MIT license.

Version 0.0.6 (September 2012)
----
Fix a bug with save_var.

Speed up insertions of large numbers of rows.

Version 0.0.5 (August 2012)
----
Make dumptruck leaner by removing demjson dependency.

Version 0.0.4 (August 2012)
----
Fix dependency crap.

Version 0.0.3 (August 2012)
----
### Remove dicti
I decided that database column case-insensitivity did not need to extend into
Python, so `dicti` has been removed, and things have been adjusted accordingly.

### Ordered Dictionaries
`DumpTruck.execute` now returns a `collections.OrderedDict` for each row rather
than a `dict` for each row. Also, order is respected on insert, so you can pass
OrderedDicts to `DumpTruck.insert` or `DumpTruck.create_table` to specify
column order.

### Index creation syntax
Previously, indices were created with

    DumpTruck.create_index(table_name, column_names)

This order was chosen to match SQL syntax. It has been changed to

    DumpTruck.create_index(column_names, table_name)

to match the syntax for `DumpTruck.insert`.

### Handling NULL values
Null value handling has been documented and tweaked.

### RowId
`dt.insert` returns the
the [rowid](http://www.sqlite.org/lang_createtable.html#rowid)
of the last row inserted row of the last row being inserted.

These webpages were helpful.

* http://ubuntuforums.org/showthread.php?t=933254
* http://www.sqlite.org/c3ref/last_insert_rowid.html

Version 0.0.2 (May 2012)
-----
I added support for unicode table names.

`DumpTruck.execute` returns data as lists of [dictis](dicti)
instead of dicts.

I fixed a few bugs that I noticed while scraping notices on
[wetland projects](https://github.com/tlevine/wetlands)

Version 0.0.1 (April 2012)
-----

Data can be inserted and retrieved as dictionaries and
lists of dictionaries.

The following column types are supported in special ways.

<table>
  <tr><th>Python type</th><th>SQLite type</th></tr>
  <tr><td>unicode</td><td>text</td></tr>
  <tr><td>str</td><td>text</td></tr>

  <tr><td>int</td><td>integer</td></tr>
  <tr><td>long</td><td>integer</td></tr>
  <tr><td>bool</td><td>boolean</td></tr>
  <tr><td>float</td><td>real</td></tr>

  <tr><td>datetime.date</td><td>date</td></tr>
  <tr><td>datetime.datetime</td><td>datetime</td></tr>

  <tr><td>dict</td><td>json text</td></tr>
  <tr><td>list</td><td>json text</td></tr>
  <tr><td>set</td><td>jsonset text</td></tr>
</table>

Indices can be created by passing a list instead of an SQL statement.

Individual variables can be saved in a variables table.

The convenience methods `.tables`, `.dump` and `.drop`
are provided for common SQL commands.

[dicti]: https://github.com/tlevine/dicti
