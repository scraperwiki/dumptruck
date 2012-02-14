<!--
To do
============
-->


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
