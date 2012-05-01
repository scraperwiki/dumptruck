To do
============

Steps
--------

In this order

1. Write more specifications.
2. Write tests.
3. Write a prototype that's just a wrapper for scraperlibs.
4. Ask people to try the prototype and give me feedback.
5. Potentially adjust the interface based on the feedback.
6. Write the real version.


Things to consider
--------------

### Database as an API
The database can be an API that allows people using different
programming languages to interact. (It is used like this on ScraperWiki.)

As such, nothing specifically Pythonic should be dumped to the database.
In particular, Highwall should use JSON instead of Pickle when
dumping to the database.

### Column types
I don't really know what scraperlibs does with types. Whatever it does
seems fine, but it might be worth documenting what happens when you save
something of a different type to a column with a different type.


### Attach
Consider whether attaching databases changes any of the pretty wrappers.

Down the line
---------------
Scraperlibs implements wrappers around only the most basic parts
of SQLite. Here are some other basic features things that could be relaxed.

* Updates
* Deletes
* Foreign keys
* Views
* Unique and non-unique indices
* Composite primary keys

These might be more advanced and thus less important to relax.

* Stored procedures
* In-memory databases
* Triggers
