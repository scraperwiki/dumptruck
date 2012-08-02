Future
------------

`DumpTruck.execute` can return a generator or a list; previously, it only
returned a list.

`DumpTruck.{get,save}_var` uses a a virtual table instead of a hacked
temporary real table that is created and deleted every time.

Make `Pickle` work properly.

Allow very long numbers to be inserted.

`DumpTruck.create_index` adds a `NOT NULL` constraint on the column if a unique
index is created.

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
