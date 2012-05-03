To do
============

Things to consider
--------------

### Database as an API
The database can be an API that allows people using different
programming languages to interact. (It is used like this on ScraperWiki.)

As such, nothing specifically Pythonic should be dumped to the database.
In particular, Highwall should use JSON instead of Pickle when
dumping to the database.

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
