Future
------------

`dt.insert` returns the
the [rowid](http://www.sqlite.org/lang_createtable.html#rowid)
of the last row inserted row of the last row being inserted.

* http://ubuntuforums.org/showthread.php?t=933254
* http://www.sqlite.org/c3ref/last_insert_rowid.html

The temporary variables table is a virtual table.

Add support for the zip data structure to `.execute` and `.insert`.
So `dt.execute('select foo from bar', datastructure = zip)` would return

    [
        [('key1', 'value1'), ('key2', 'value2')]
    ]

and `dt.insert([('hattype', 'hardhat'), ('color', 'pink')])` would be
equivalent to `dt.insert(dict([('hattype', 'hardhat'), ('color', 'pink')]))`.

Make `Pickle` work properly.

Allow very long numbers to be inserted.

Version 0.0.2
-----

Add support for unicode table names.

`DumpTruck.execute` returns data as lists of [dictis](dicti)
instead of dicts.

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
