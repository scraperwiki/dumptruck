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

#### Output to a table
You might want to store the output of a query in the database.
If this is what you want to do, ...

1. Maybe it's an option to `Highwall.execute`
2. Consider whether the result should rewrite or append to the table in which it is to be stored.
3. Or maybe an error is raised if the table already exists.



#### Index objects
Highwall allows you to manage indices as if they were
normal Python objects.

First, create an index object, specifying the columns.

    i1=Index('modelNumber')

You can specify multiple single-column indices by passing a list of column names.

    h.index_list['machines']=Index(['modelNumber','serialNumber'])

#### Managing indices
There are two methods for managing indices,
`Highwall.index_list` and `Highwall.index_info`.

`Highwall.index_list` lets you access indices by table.
It acts like a dictionary. Here's how you specify an index.

    i=Index('modelNumber')
    h.index_list['machines']['machines_modelNumber'] = i

This adds an index on the `modelNumber` column to the `machines` table.
In SQLite, all indices have names; in this case, the index is named `machines_modelNumber`.

If you want a unique index, do this.

    i2=Index('year',unique=True)
    h.index_list['models']['model_year'] = i2

If you specify a column that already contains non-distinct values, you will receive an error.

We can retrieve a dictionary of all indices for the `machines` table like so.

    print(h.index_list['machines'])

And we can retrieve a dictionary of indices by table for the whole database like so.

    print(h.index_list)

We can retrieve them as a dictionary and save them somewhere else.

    d=h.index_list

We can delete an the index like we delete a normal dictionary value.

    del(h.index_list['machines']['machines_modelNumber'] )

We can delete all indices on a particular table.

    del(h.index_list['machines'])

`Highwall.index_info` acts like `Highwall.index_list`
except that indices are not organized by table.
You can use it to retrieve indices by name without specifying the table name.

    print(h.index_info['machines_modelNumber'])

This returns a dictionary containing a `table_name` and an `index`.

You can set indices by assigning a tuple or a dict to Highwall.index_info.
Either way, it should have two elements; a tuple should have an Index
object followed by a table name, and a dict should have an `index` key
and a `table_name` key. For example, here are three equivalent index assignments.

    i2=Index('year',unique=True)
    h.index_list['models']['model_year'] = i2
    h.index_info['model_year'] = (i2, 'models')
    h.index_info['model_year'] = {'index':i2, 'table_name':'models')

