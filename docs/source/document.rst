FIS-B Rest
==========

Basic Return Structure
----------------------

The only JSON field guaranteed to be in each returned object is ``status``.
It will have one of two values: 0 if there were no errors, and -1, if
there were any errors. Note that this does not include regular web
errors like 404 errors. Just errors where the query was close enough
that a JSON object was returned.

If you do get an ``status`` code of -1, you will also get an ``error``
field which contains an error message.

For example: ::

  http://127.0.0.1:5000/taf/kind?lat=80

would return: ::

  {
    "error": "Need both lat and long parameters. ",
    "status": -1
  }

If the ``status`` code is 0, you will get an object that contains
``num_results`` and ``after`` fields.

For example: ::
  http://127.0.0.1:5000/taf/kingtut

returns: ::

  {
    "after": "2004-01-01T00:00:00Z",
    "num_results": 0,
    "status": 0
  }

``num_results`` is pretty obvious. If there were any results, we would return a ``result`` or ``results``
field depending on the query. We will cover this more in a minute.

**The use of the 'after' field is critical to understand**. Each non-error FIS-B data query 
will return an ``after`` field. You can use this value in a query string to return only
those results which occurred *after* the ``after`` time.

To get the most recent METAR for KIND: ::

  http://127.0.0.1:5000/metar/kind

might return: ::

  {
    "after": "2021-06-23T02:03:41.221000Z",
    "num_results": 1,
    "result": {
        "contents": "METAR KIND 230154Z 20006KT 10SM FEW065 FEW250 17/08 A3003
                     RMK AO2 SLP168\n     T01720083=",
        "expiration_time": "2021-06-23T03:54:00Z",
        "observation_time": "2021-06-23T01:54:00Z",
        "type": "METAR",
        "unique_name": "KIND"
    },
    "status": 0
  }

If we wanted to get the most recent KIND METAR we can just repeat the query.
But if we wanted a result only if a new METAR has been posted, we would
add the ``after`` query string: ::

  http://127.0.0.1:5000/metar/kind?after=2021-06-23T02:03:41.221000Z

If there is no new result, we will get: ::

  {
    "after": "2021-06-23T02:03:41.221000Z",
    "num_results": 0,
    "status": 0
  }

Once a new result arrives, we will get the full result.

A couple of points about the ``after`` parameter:

* **Always use an 'after' value you got from FIS-B Rest**. Don't 
  make them up. This ensures you will always get the latest result.

* If you get a new result, it means something changed from the old
  result. Maybe a new image, maybe a NOTAM that didn't 
  have any text changes but 
  was resent and has a new expiration time.

Result and Results
------------------

There are two basic types of rest queries allowed: those that return
a single result, and those that may return more than a single result.
Queries that can at most return a single result will return the
result as a dictionary in the ``result`` field. If the query *might*
return more than one result, it will return a list in the ``results``
field. Note the difference in name. If a query that can return more
than one result only returns one result, it will still return a 
``results`` field with a list containing only one item in it. The documentation
will clearly state for each query if it will return only one, or more than
one item.

See the METAR example above as an example of a query only returning
one item. If we sent: ::

  http://127.0.0.1:5000/metar

We would get back a ``results`` field with a list of many results. ::

  {
    "after": "2021-06-23T03:09:30.380000Z",
    "num_results": 549,
    "results": [
        {
            "contents": "METAR KMWK 230135Z AUTO 00000KT 10SM CLR 18/14
                         A3003 RMK AO2\n     T01820144=",
            "expiration_time": "2021-06-23T03:35:00Z",
            "observation_time": "2021-06-23T01:35:00Z",
            "type": "METAR",
            "unique_name": "KMWK"
        },
        {
            "contents": "METAR KOSH 230153Z 00000KT 10SM BKN070 17/10 A2993=",
            "expiration_time": "2021-06-23T03:53:00Z",
            "observation_time": "2021-06-23T01:53:00Z",
            "type": "METAR",
            "unique_name": "KOSH"
        }

        << many results removed >>
        
   ],
    "status": 0
  }

Query Strings
-------------



