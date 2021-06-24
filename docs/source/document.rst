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

The only exception to the ``after`` field are 'static' requests. These are requests that don't
reference FIS-B data, but other static data. You can always tell these requests because the
first part of the request will start with ``/static/``. For example, the request to get a list
of the legend colors for all images is requested by: ::

  http://127.0.0.1:5000/static/legend

Static requests are exactly like any other request, except they will not return
an ``after`` field, and supplying one to a request will have no effect.

Returning to the topic of FIS-B requests, to get the most recent METAR for KIND: ::

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
result as an object (dictionary) in the ``result`` field. If the query *might*
return more than one result, it will return a list of objects in the ``results``
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

Query strings appear after a question mark ('``?``') in a request and had a name,
an equal sign ('``=``'), are followed with a value. Multiple query strings are
separated by ampersand ('``&``') characters.

In FIS-B Rest, query parameters will modify the request in some way. Most
query parameters only affect a small portion of requests. In the description
of each request there will be a list of which parameters are associated with
each request and what actions they perform.

**after**
  Will return results that were created after this value. This value
  should be obtained **ONLY** from the ``after`` field of a returned
  JSON object. This field applies to all non-static rest queries.

  Form: ::

    after=<value from 'after' field from returned JSON object>

  Example: ::

    http://127.0.0.1:5000/metar?after=2021-06-23T22:21:43.282000Z

**high, low**
  Will return objects only if they are between two altitude limits
  given in feet (inclusive). Only applies to objects that have a 
  graphic component. They must always occur together, must be 
  positive integers and low must be <= high.

  Typically, this applies to WST, G-AIRMET, SIGMET, AIRMET,
  NOTAM-TRA, and NOTAM-TFR. It does not apply to NOTAM-D-SUA
  (for complicated reasons discussed when we describe this
  type of object).

  Warning: Some TWGO (Text with Graphic Overlays) objects will
  get a text segment before the graphic portion arrives. So the
  query will not catch the altitude limits. Since the object
  could not possibly meet criteria (see next paragraph), it will
  be returned.

  These query strings will not filter out any objects to which
  they do not apply. So if you do a query on METARs, or
  TWGO objects that don't have any altitude information, the
  selected objects will be returned.

  Form: ::

    low=<low altitude value>&high=<high altitude value>

  Example: ::

    http://127.0.0.1:5000/g-airmet?low=12000&high=17999


**lat, lon**
  If a latitude and a longitude is provided, AND the selected object is A
  polygon or a set of polygons, the object will be returned only if
  the latitude and longitude are within the polygon. You mist
  supply both a latitude and longitude (as integer or floating point
  values) and they must have valid values (latitude -90 to 90,
  longitude -180 to 180).

  These query strings will not filter out any objects to which
  they do not apply. So if you do a query on METARs, or
  TWGO objects that are not polygons, the
  selected objects will be returned.

  Form: ::

    lat=<latitude>&lon=<longitude>

  Example: ::

    http://127.0.0.1:5000/notam-d-sua?lat=40.1234&lon=-86.1234

**limit**
  Will limit the number of items returned to the specified
  amount. This only makes sense for those queries that may return
  more than one object. The number must be an integer >= 1.
  There is a default limit of 10,000 for all queries (more than
  you will ever need). If you specify a value higher than this,
  it will be reduced to 10,000.

  Form: ::

    limit=<maximum objects to return>

  Example: ::

    http://127.0.0.1:5000/all?limit=500

FISB Object Principles
----------------------

We will next discuss the individual REST directives
and the results they return. Different objects have
fields depending on their type, but all objects have
a number of fields in common. We will discuss those
here and not mention again.

Again, there are two types of REST requests, those that
are FIS-B related, and those that are static. The fields
mentioned below are only FIS-B related.

**expiration_time**
  Time the message should expire in ISO-8601 UTC. FISB Rest will
  not send an update when an object expires. That is up to you.
  All objects will have this field.

**type**
  Basic type of message. These are items like ``METAR``, ``TAF``, ``NOTAM``,
  ``WST``, ``G-AIRMET``, etc. The type of a message dictates the fields
  that it will have. All objects will have this field.

**unique_name**
  This is a unique identifier within a particular 'type'. If you combine
  the 'type' and 'unique_name' strings you will get a primary key valid
  across all FISB objects. Internally, FISB Rest combines the
  'type' and 'unique_name' fields with a dash to get internal
  primary key.
  All objects will have this field.

**geojson**
  All graphical objects other than images (i.e. objects with vector data)
  will have a 'geojson' field. This is in standard geojson format.
  **ALL** geojson objects have at their outer layer a ``FeatureCollection``
  with a ``features`` list. The ``features`` list will have one or more
  geojson ``Feature`` objects. This even includes object types like METARs
  that will only have one ``Feature``. The reason behind this is to
  make vector object processing more uniform.

  Polygon and Point objects are common. G-AIRMET can produce both Polygons
  and LineStrings. Each ``FeatureCollection`` will only have one type of
  geometry.

  The ``properties`` field will vary dependent on the 'type' of object. These
  will be documented for each individual object type.

  An example of the 'geojson' field and the others described above is: ::

    {
      "type": "METAR",
      "unique_name": "K4M9"
      "observation_time": "2021-06-24T02:35:00Z",
      "contents": "METAR K4M9 240235Z AUTO 00000KT 10SM CLR 24/24
                   A3004 RMK AO2 PWINO=",
      "expiration_time": "2021-06-24T04:35:00Z",
      "geojson": {
          "features": [
              {
                  "geometry": {
                      "coordinates": [
                          -90.648,
                          36.404
                      ],
                      "type": "Point"
                  },
                  "properties": {
                      "id": "K4M9",
                      "name": "K4M9"
                  },
                  "type": "Feature"
              }
          ],
          "type": "FeatureCollection"
      },
    }

**cancel**
  This field **only** applies to TWGO objects. This includes 'type' field values of:

  * ``NOTAM`` (all subtypes)
  * ``FIS_B_UNAVAILABLE`` (FIS-B Product Unavailable)
  * ``AIRMET``
  * ``SIGMET``
  * ``WST`` (Convective Sigmet)
  * ``CWA`` (Center Weather Advisory),
  * ``SUA`` (Not the NOTAM-D SUA, but the old SUA message)
  * ``G_AIRMET``
  
  If this field is present in a message, the message must be cancelled. It is only
  present in messages being cancelled.
  In practice, I have only seen messages cancelled for
  NOTAMS, G-AIRMETS, and CWAs. But the standard states all TWGO messages are fair game.

  The value of the 'cancel' field is just the
  'unique_name' field. You should immediately delete the message of the
  specified 'type' and 'unique_name' from your database.

  **Whenever you get one of the TWGO 'type' fields, the first thing you should do is to check
  the object for a 'cancel' field.** If you find one, cancel the message (which might
  not even exist in your records), and do no further processing on the message. All
  the other fields are not important.

  Here are a couple of examples of messages with the 'cancel' field present. A
  G-AIRMET cancellation: ::

    {
        "type": "G_AIRMET",
        "unique_name": "21-9897"
        "cancel": "21-9897",
        "expiration_time": "2021-06-21T17:10:21Z",
    }

  And a NOTAM cancellation: ::

    {
        "type": "NOTAM",
        "unique_name": "21-12860"
        "cancel": "21-12860",
        "expiration_time": "2021-06-21T17:23:18Z",
    }

