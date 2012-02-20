Highwall
==============

Highwall is an document-like interface to an SQLite database that lets you relax.
It supports the following database formats.

Quick start
----------
Highwall helps you relax by making relational databases
feel more like document databases.

### Install

    # This doesn't actually work yet; this here so I don't forget
    # to put it in once I put it on PyPI once it's ready.
    pip install highwall

### Initialize

Open the database connection by initializing the a Highwall object

    h = Highwall()

### Save
The simplest `insert` call looks like this.

    h.insert({"firstname":"Thomas","lastname":"Levine"},"diesel-engineers")

This saves a new row with "Thomas" in the "firstname" column and
"Levine" in the "lastname" column. It uses the table "diesel-engineers"
inside the database "highwall.db". It creates or alters the table
if it needs to.

### Retrieve
Once the database contains data, you can retrieve them.

    data=h.execute('SELECT * FROM `diesel-engineers`')

The data come out as a list of dictionaries, with one dictionary per row.


Slow start
-------
### Initialize

You can specify a few of keyword arguments when you initialize the Highwall object.
For example, if you want the database file to be `bucket=wheel-excavators.db`,
you can use this.

    h = Highwall(dbname="bucket-wheel-excavators.db")

It actually takes up to three keyword arguments.

    Highwall(dbname='highwall.db',auto_commit=True,vars_table="_highwallvars")

* `dbname` is the database file to save to; the default is highwall.db.
* `vars_table` is the name of the table to use for `Highwall.get_var`
and `Highwall.save_var`; default is `_highwallvars`. Set it to `None`
to disable the get_var and save_var methods.
* `auto_commit` is whether changes to the database should be automatically committed;
if it is set to `False`, changes must be committed with the `commit` method
or with the `commit` keywoard argument.

### Saving
As discussed earlier, the simplest `insert` call looks like this.

    h.insert({"firstname":"Thomas","lastname":"Levine"})

But you can also pass a list of dictionaries.

    data=[
        {"firstname":"Thomas","lastname":"Levine"},
        {"firstname":"Julian","lastname":"Assange"}
    ]
    h.insert(data)

You can even past nested structures; dictionaries,
sets and lists will automatically be dumped to JSON.

    data=[
        {"title":"The Elements of Typographic Style","authors":["Robert Bringhurst"]},
        {"title":"How to Read a Book","authors":["Mortimer Adler","Charles Van Doren"]}
    ]
    h.insert(data)

It would be cool if I can come up with a way for `h.insert` to return
the [rowid](http://www.sqlite.org/lang_createtable.html#rowid)(s) of the
row(s) that are being saved. Dunno how annoying this would be....

### Individual values
It's often useful to be able to quickly and easily save one metadata value.
For example, you can record which page the last run of a script managed to get up to.

    h.save_var('last_page', 27)
    27 == h.get_var('last_page')

It's stored in a table that you can specify when initializing Highwall.
If you don't specify one, it's stored in `_highwallvars`.

If you want to save anything other than an int, float or string type,
use json or pickle.

### Helpers
Highwall provides specialized wrapper around some common commands.

`Highwall.show_tables` returns a set of all of the tables in the database.

    h.show_tables()

`Highwall.drop` drops a table.

    h.drop("diesel-engineers")

### Indices

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

### Delaying commits
By default, the `insert`, `get_var`, `drop` and `execute` methods automatically commit changes.
You can stop one of them from committing by passing `commit=False` to the method.
Commit manually with the `commit` method.  For example:

    h=Highwall()
    h.insert({"name":"Bagger 293","manufacturer":"TAKRAF","height":95}, commit=False)
    h.save_var('page_number', 42, commit=False)
    h.commit()

When you use `Highwall.index_info` or `Highwall.index_list`,
your changes are automatically committed. If you need to delay the commits,
you can use the underlying getter method, passing a `commit = True` keyword argument.
