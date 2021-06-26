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

**after=**
  Will return results that were created after this value. This value
  should be obtained **ONLY** from the ``after`` field of a returned
  JSON object. This field applies to all non-static rest queries.

  Form: ::

    after=<value from 'after' field from returned JSON object>

  Example: ::

    http://127.0.0.1:5000/metar?after=2021-06-23T22:21:43.282000Z

**high=, low=**
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


**lat=, lon=**
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

**limit=**
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

``"expiration_time"``
  Time the message should expire in ISO-8601 UTC. FISB Rest will
  not send an update when an object expires. That is up to you.
  All objects will have this field.

``"type"``
  Basic type of message. These are items like ``METAR``, ``TAF``, ``NOTAM``,
  ``WST``, ``G-AIRMET``, etc. The type of a message dictates the fields
  that it will have. All objects will have this field.

``"unique_name"``
  This is a unique identifier within a particular 'type'. If you combine
  the 'type' and 'unique_name' strings you will get a primary key valid
  across all FISB objects. Internally, FISB Rest combines the
  'type' and 'unique_name' fields with a dash to get internal
  primary key.
  All objects will have this field.

``"geojson"``
  All graphical objects other than images (i.e. objects with vector data)
  will have a 'geojson' field. This is in standard geojson format.
  **ALL** geojson objects have at their outer layer a ``FeatureCollection``
  with a ``features`` list. The ``features`` list will have one or more
  geojson ``Feature`` objects. This even includes object types like METARs
  that will only have one ``Feature``. The reason behind this is to
  make vector object processing more uniform.

  Polygon and Point objects are common. G-AIRMET can produce both Polygons
  and LineStrings. So can PIREPs (almost all PIREPs are point objects,
  but you can have a 'route' PIREP which will be rendered as a
  LineSting). Each ``FeatureCollection`` will only have one type of
  geometry.

  Also note that some objects can have more than one geometry. The principle
  is that fields outside of a geojson field apply to the entire object,
  but ``"properties"`` within a geojson object apply only to that geography.
  They may also apply to the entire object (placed there to benefit a mapping
  API), but they don't have to.
  The ``"properties"`` field will vary dependent on the 'type' of object. These
  will be documented for each individual object type except for a few common
  items discussed here.

  There are a number of ``"geojson"`` ``"properties"`` fields that are common
  enough to be discussed now.

    ``"altitudes"``
      List of 4 items: Highest altitude, highest altitude
      type (MSL or AGL), lowest altitude, and lowest altitude type (MSL or AGL).
      Except for NOTAM-TMOA and NOTAM-TRA, both altitude types will be the same.

    ``"start_time"``
      Start time of the activity. This may be different than
      any time mentioned in the encompassing object. May not have an
      accompanying ``"stop_time"``.

    ``"stop_time"``
      Stop time of the activity. This may be different than
      any time mentioned in the encompassing object. May not have an
      accompanying ``"start_time"``.

  A common scenario that occurs is in NOTAM-TFRs. Imagine a VIP is travelling
  to a city, then going to a convention center to give a speech, and then
  traveling back to the airport. A NOTAM-TFR will be issued with three
  geographies: one each (with identical coordinates) for arrival and departure
  at the airport, and one for the convention center. Each will have different
  start and stop times, and the altitudes for the convention center speech
  might be different than the airport altitudes.
  
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
                  },
                  "type": "Feature"
              }
          ],
          "type": "FeatureCollection"
      },
    }

``"cancel"``
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

  Note that the NOTAM won't have a 'subtype' field. It isn't
  needed. The 'unique_id' is sufficient and will work across 
  all NOTAM subtypes.

``"station"``
  Some objects, such as CRL and RSR objects are dependent on a 
  particular ground station. The best identifier for the station
  is its latitude and longitude. The value of the ``"station"``
  field is the latitude and longitude combined with a tilde
  character such as ``'40.0383~-86.255593'``. One advantage of
  this scheme is that the standard in some cases requires you
  to show the latitude and longitude of all stations, and 
  you can un-parse the ground station id to get this information.

REST API and Message Descriptions
---------------------------------

All items
^^^^^^^^^
::

  /all

Will return all current reports. This is essentially a dump of the
database. 

The way this is typically used is to perform an ``/all`` at the start,
then use use the ``"after"`` field to get periodic updates. If you don't
want to get all results at once, you can use the 'after=' and 'limit='
query parameters together.

METARs
^^^^^^
::

  /metar
  /metar/<4 character id>

Return all METAR reports or a single METAR report.

Example: ::

  {
        "type": "METAR",
        "unique_name": "KLAF"
        "observation_time": "2021-06-24T16:54:00Z",
        "contents": "METAR KLAF 241654Z VRB06G17KT 10SM CLR 28/16
                     A3004 RMK AO2 SLP168\n     T02780161=",
        "expiration_time": "2021-06-24T18:54:00Z",
        "geojson": {
            "features": [
                {
                    "geometry": {
                        "coordinates": [
                            -86.9475,
                            40.4125
                        ],
                        "type": "Point"
                    },
                    "properties": {
                        "id": "KLAF",
                        "name": "KLAF"
                    },
                    "type": "Feature"
                }
            ],
            "type": "FeatureCollection"
        },
  }

Notes:

* Will have a ``"geojson"`` field if configured for locations. This
  will always be a 'Point'.
* ``"observation_time"``: Time the observation was made.
* The expiration time is typically 2 hours after the observation time.

TAFs
^^^^
::

  /taf
  /taf/<4 character id>

Return all TAF reports, or a single report.

Example: ::

  {
    "type": "TAF",
    "unique_name": "KIND",
    "issued_time": "2021-06-24T11:20:00Z",
    "valid_period_begin_time": "2021-06-24T12:00:00Z",
    "valid_period_end_time": "2021-06-25T18:00:00Z"
    "contents": "TAF KIND 241120Z 2412/2518 16007KT P6SM FEW200\n
                 FM241900 19012G20KT P6SM SCT250\n
                 FM250600 18010KT P6SM VCSH OVC100\n
                 FM251500 19014G22KT P6SM VCSH OVC045\n
                 FM251700 20014G23KT P6SM VCSH OVC028=",
    "expiration_time": "2021-06-25T18:00:00Z",
    "geojson": {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        -86.2816,
                        39.72518
                    ],
                    "type": "Point"
                },
                "properties": {
                    "id": "KIND",
                    "name": "KIND"
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    },
  }

Notes:

* Will have a ``"geojson"`` field if configured for locations. This
  will always be a 'Point'.
* ``"issued_time"``: Time the forecast was issued by NWS.
* ``"valid_period_begin_time"``: Starting time of the forecast.
* ``"valid_period_end_time"``: Ending time of the forecast. This is
  also the expiration time.

Winds Aloft Forecasts
^^^^^^^^^^^^^^^^^^^^^

::

  /wind-06
  /wind-06/<3 character id>
  /wind-12
  /wind-12/<3 character id>
  /wind-24
  /wind-24/<3 character id>

Return winds aloft forecast for all stations or a single station. 
Winds aloft forecasts are issued 6, 12, and 24 hours in advance.
Wind forecasts use a 3 character id, rather than 4.

Example: ::

  {
    "type": "WINDS_12_HR",
    "unique_name": "CMH",
    "model_run_time": "2021-06-24T12:00:00Z",
    "issued_time": "2021-06-24T13:58:00Z",
    "valid_time": "2021-06-25T00:00:00Z"
    "for_use_from_time": "2021-06-24T21:00:00Z",
    "for_use_to_time": "2021-06-25T06:00:00Z",
    "contents": "   1919 2122+13 2712+11 9900+04 2606-09 3109-19
                    292735 312945 315757",
    "expiration_time": "2021-06-25T06:00:00Z",
  }

Notes:

* Will have a 'Point' ``"geojson"`` field if configured for location.
* The header is not provided since there are multiple options
  for display. A typical header could look like: ::

    3000    6000    9000   12000   18000   24000  30000  34000  39000
    1919 2219+17 2217+12 2208+04 3012-09 2819-20 281435 363145 317257
* ``"model_run_time"``: Time the winds aloft model was run to generate
  the report.
* ``"issued_time``": When the report was issued.
* ``"valid_time``": Time at which the forecast is designed to model. This
  is a single point in time.
* ``"for_use_from_time"``: Starting time the forecast can be used.
* ``"for_use_to_time"``: Time the forecast should no longer be used.
  This is also the expiration time.

PIREPs
^^^^^^

::

  /pirep

Returns all available PIREPs.
Will have a ``"geojson"`` field if configured for location. This is most
commonly a 'Point', but in the case of a route, may also be a LineString.

Example of a PIREP that is a Point: ::

  {
    "type": "PIREP",
    "unique_name": "djfHdke8mQ2Z"
    "contents": "PIREP MSN 241940Z MSN UA /OV MSN080020/TM 1940/FL220/TP
                 E545/TA M15/IC LGT RIME DURD 220-180",
    "expiration_time": "2021-06-24T21:40:00Z",
    "fl": "220",
    "ic": "LGT RIME DURD 220-180",
    "ov": "MSN080020",
    "report_time": "2021-06-24T19:40:00Z",
    "report_type": "UA",
    "station": "MSN",
    "ta": "M15",
    "tm": "1940",
    "tp": "E545",
    "geojson": {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        -88.895286,
                        43.218243
                    ],
                    "type": "Point"
                },
                "properties": {
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
      },
  }

Example of a PIREP that is a route with a geojson type of LineString: ::

  {                                                                       
    "type": "PIREP",
    "unique_name": "KQeZQflpleq1"
    "ov": "ACO090020-ACO310010",
    "report_time": "2021-06-25T10:32:00Z",
    "report_type": "UA",
    "station": "AKR",
    "tb": "LGT-MOD 350-390",
    "tm": "1032",
    "tp": "NMRS",
    "fl": "350",
    "contents": "PIREP ACO 251032Z AKR UA /OV ACO090020-ACO310010
                 /TM 1032/FL350/TP NMRS/TB LGT-MOD 350-390",
    "expiration_time": "2021-06-25T12:32:00Z",
    "geojson": {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        [-80.765163, 41.156786],
                        [-81.38991, 41.194716]                                               
                    ],
                    "type": "LineString"
                },
                "properties": {
                    "id": "KQeZQflpleq1"
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    },
  }

Notes:

* While FIS-B Decode can parse about 90-95% of all locations, it can not
  parse them all. PIREPs (especially by tower controllers) do not always
  follow a set format, since they can be hand entered.
* ``"station"``: Nearest weather reporting location.
* ``"report_type"``: Either ``UA`` for normal PIREP or ``UUA`` for urgent.
* ``"report_time"``: Time the report was made. There are two ways FIS-B
  Decode can be configured. The way the standard suggests is to just keep
  the report active until an hour or so after it is last transmitted.
  This can result in PIREPs hanging around for 4 hours or more. It can
  also be configured to delete the PIREP so many minutes after the report
  time (2 hours is a good value). This is the preferred method.
* The identifier immediately after 'PIREP' ('PIREP MSN' in our example)
  is totally made-up garbage by the FIS-B creator. Do not use it. The
  ``"station"`` field is from the FAA and is safe to use.
* The report is parsed into its basic fields. If a field name is not
  in the report, it will not be listed. These are:

    * ``"ov"``: Location of the PIREP.
    * ``"tm"``: Time the PIREP activity occurred or was reported.
    * ``"fl"``: Flight level.
    * ``"tp"``: Type of aircraft.
    * ``"tb"``: Turbulence report.
    * ``"sk"``: Sky conditions.
    * ``"rm"``: Remarks.
    * ``"wx"``: Flight visibility and flight weather.
    * ``"ta"``: Temperature.
    * ``"wv"``: Wind direction and speed.
    * ``"ic"``: Icing report.

SIGMET, AIRMET, WST, CWA
^^^^^^^^^^^^^^^^^^^^^^^^

::

  /sigmet
  /airmet
  /wst
  /cwa

Provides all available SIGMETs, AIRMETs, WSTs (Convective SIGMETS), and
CWAs (Center Weather Advisory). From a returned object perspective,
they are all identical except for their subject matter.

One important thing to remember is that all of these objects can
have both a text and object portion. Only the text portion is mandatory.
Per the standard, if a text portion is received, it is immediately sent
out. If a graphic portion arrives, it is combined with the text portion
and both are sent out as a single report. If a graphic portion never
gets a matching text portion, it is never sent out.

In the example below, the only difference if this was only a text only
AIRMET would be that the ``"geojson"`` field would be missing.

Example: ::

  {
    "type": "AIRMET",
    "unique_name": "21-9178"
    "issued_time": "2021-06-24T20:31:00Z",
    "for_use_from_time": "2021-06-24T20:45:00Z",
    "for_use_to_time": "2021-06-25T03:00:00Z",
    "contents": "AIRMET KBOS 242031 BOST WA 242045\nAIRMET TANGO UPDT
                 3 FOR TURB VALID UNTIL 250300\nAIRMET TURB...ME NH VT
                 MA RI CT NY LO NJ PA OH LE WV MD DC DE VA\nNC SC GA FL
                 AND CSTL WTRS\nFROM 80NW PQI TO CON TO 80ESE SIE TO
                 30ENE ILM TO 20W CTY TO\n130ESE LEV TO 40W CEW TO 50SW
                 PZD TO GQO TO HMV TO HNN TO CVG TO\nFWA TO 30SE ECK TO
                 YOW TO YSC TO 80NW PQI\nMOD TURB BTN FL270 AND FL430.
                 CONDS CONTG BYD 03Z THRU 09Z.",
    "expiration_time": "2021-06-25T03:00:00Z",
    "geojson": {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        [-69.494019, 47.707443],
                        [-71.575241, 43.219528],
                        [-73.22525, 38.574371],
                        [-77.313538, 34.541016],
                        [-83.431549, 29.597855],
                        [-87.830887, 28.326874],
                        [-87.454605, 30.823517],
                        [-84.979935, 31.063843],
                        [-85.152969, 34.961243],
                        [-82.128983, 36.436844],
                        [-82.025986, 38.753586],
                        [-84.70253, 39.015884],
                        [-85.187988, 40.979004],
                        [-82.235413, 42.900925],
                        [-75.896301, 45.441513],
                        [-71.690598, 45.43808],
                        [-69.494019, 47.707443]
                      ],
                    "type": "Polygon"
                },
                "properties": {
                    "altitudes": [
                        43000,
                        "MSL",
                        27000,
                        "MSL"
                    ],
                    "id": "21-9178",
                    "start_time": "2021-06-24T20:45:00Z",
                    "stop_time": "2021-06-25T03:00:00Z"
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    },
  }

Notes:

* ``"cancel"``: Present only when cancelled. Always check for this first
  and delete the report. No other processing required.
* ``"issued_time``": When the report was issued.
* ``"valid_time``": Time at which the forecast is designed to model. This
  is a single point in time.
* ``"for_use_from_time"``: Starting time the forecast can be used.
* ``"for_use_to_time"``: Time the forecast should no longer be used.
  This is also the expiration time.
* **lat=** and **lon=** are valid query strings. If present, only those
  results which contain the supplied point will be returned.
* **high=** and **low=** are valid query strings. If present, only those
  results that fall within a certain altitude range will be returned.

G-AIRMET
^^^^^^^^

::

  /g-airmet
  /g-airmet-00
  /g-airmet-03
  /g-airmet-06

Return all G-AIRMETS. The 00, 03, and 06 variants will only return G-AIRMETs
of that type.

Example: ::

  {
    "type": "G_AIRMET",
    "unique_name": "21-10892"
    "subtype": 0,
    "issued_time": "2021-06-25T02:45:00Z",
    "for_use_from_time": "2021-06-25T03:00:00Z",
    "for_use_to_time": "2021-06-25T06:00:00Z",
    "expiration_time": "2021-06-25T06:00:00Z",
    "geojson": {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        [-84.529495, 46.609497],
                        [-86.84967, 45.799942],
                        [-87.399673, 44.399872],
                        [-84.859772, 43.919907],
                        [-82.389908, 45.259552],
                        [-84.529495, 46.609497]
                    ],
                    "type": "Polygon"
                },
                "properties": {
                    "altitudes": [
                        2000,
                        "AGL",
                        0,
                        "AGL"
                    ],
                    "element": "LLWS",
                    "id": "21-10892",
                    "start_time": "2021-06-25T03:00:00Z",
                    "stop_time": "2021-06-25T06:00:00Z"
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    },
  }

Notes:

* ``"cancel"``: Present only when cancelled. Always check for this first
  and delete the report. No other processing required.
* ``"subtype"``: One of 0, 3, or 6, dependent if this is a 00, 03, or 06
  hour G-AIRMET. '/g-airmet' will select all of these. '/g-airmet-00', 
  '/g-airmet-03', and '/g-airmet-06' will only select a particular type.
* ``"issued_time``": When the report was issued.
* ``"for_use_from_time"``: Starting time the forecast can be used.
* ``"for_use_to_time"``: Time the forecast should no longer be used.
  This is also the expiration time.
* There is only a single graphical entry for each G-AIRMET.
* Most G-AIRMETs return Polygons, but freezing level G-AIRMETs
  may return a Polygon or LineString.
* The ``"properties"`` geojson field may contain the following fields:
   ``"conditions"``
      If the reason for the G-AIRMET is IFR or mountain Obscuration
      conditions, this field will list the conditions responsible. This
      will be a list with one or more of the following elements:
      
        * ``'UNSPCFD'``: Unspecified
        * ``'ASH'``: Ash
        * ``'DUST'``: Dust
        * ``'CLOUDS'``: Clouds
        * ``'BLSNOW'``: Blowing snow
        * ``'SMOKE'``: Smoke
        * ``'HAZE'``: Haze
        * ``'FOG'``: Fog
        * ``'MIST'``: Mist
        * ``'PCPN'``: Precipitation

   ``"element"``
      Single string present for each G-AIRMET which describes the reason
      it was issued. These will be one of:
      
        * ``'TURB'``: Turbulence
        * ``'LLWS'``: Low level wind shear
        * ``'SFC'``: Strong surface winds
        * ``'ICING'``: Icing
        * ``'FRZLVL'``: Freezing Level
        * ``'IFR'``: IFR conditions
        * ``'MTN'``: Mountain Obscuration

* **lat=** and **lon=** are valid query strings. If present, only those
  results which contain the supplied point will be returned.
* **high=** and **low=** are valid query strings. If present, only those
  results that fall within a certain altitude range will be returned.


NOTAM (in general)
^^^^^^^^^^^^^^^^^^

::

/notam
/notam/<4 character id>

Lists all NOTAMs of all types. If an id is specified, will find all
NOTAMs associated with that id (i.e. the ``"location"`` field inside
a NOTAM). Not all NOTAMs have a location.

No examples will be given for this section. See the more detailed types
of NOTAMs for examples.

There are basically two types of FIS-B NOTAMs. NOTAM-TFRs and all the rest.
NOTAM-TFRs in FIS-B are repackaged by the FIS-B creator and have differences
with the other NOTAMs in terms of format.

I further divide NOTAM-Ds into two type: regular NOTAM-Ds and NOTAM-D-SUA.
The NOTAM-D-SUAs are different, because they have an optional location field
that is not produced by FIS-B, but loaded as an auxillary file. They also
have some unique characteristics which must be considered.

Fields common to all NOTAMs:

* ``"subtype"``: The type of NOTAM. Will be one of:

  * ``"TFR"``: NOTAM-TFR
  * ``"D"``: NOTAM-D
  * ``"D-SUA"``: NOTAM-D with SUA information.
  * ``"FDC"``: NOTAM-FDC

* ``"number"``: This is the 'official' number of the NOTAM. It is what
  should be shown to users. Do not use the ``"unique_name"``.

Notes:

* ``"cancel"``: Present only when cancelled. Always check for this first
  and delete the report. No other processing required.

  
NOTAM-TFR
^^^^^^^^^

::

/notam-tfr

NOTAM-TFRs may or may not be associated with a geojson object. If they
are, the object may have multiple components.

NOTAM-TFRs are truncated after a certain number of characters and will end with
the text ``'(INCMPL)'``.

Example: ::

  {
    "type": "NOTAM",
    "unique_name": "0-5116"
    "subtype": "TFR",
    "number": "0/5116",
    "contents": "NOTAM-TFR 0/5116 220551Z PART 1 OF 4 SECURITY..SPECIAL
                SECURITY INSTRUCTIONS FOR UNMANNED AIRCRAFT SYSTEM (UAS)
                OPERATIONS FOR MULTIPLE LOCATIONS NATIONWIDE. THIS NOTAM
                REPLACES NOTAM FDC 9/7752 TO PROVIDE UPDATED INSTRUCTIONS.
                PURSUANT TO 49 U.S.C. SECTION 40103(B)(3), THE FAA CLASSIFIES
                THE AIRSPACE DEFINED IN THIS NOTAM AND IN FURTHER DETAIL AT
                THE FAA WEBSITE IDENTIFIED BELOW AS 'NATIONAL DEFENSE
                AIRSPACE'. OPERATORS WHO DO NOT COMPLY WITH THE FOLLOWING
                PROCEDURES MAY FACE THE FOLLOWING ENFORCEMENT ACTIONS: THE
                UNITED STATES GOVERNMENT MAY PURSUE CRIMINAL CHARGES,
                INCLUDING CHARGES UNDER 49 U.S.C. SECTION 46307; AND THE
                FAA MAY TAKE ADMINISTRATIVE ACTION, INCLUDING IMPOSING
                CIVIL PENALTIES AND REVOKING FAA CERTIFICATES OR
                AUTHORIZATIONS TO OPERATE UNDER TITLE 49 U.S.C. SECTIONS
                44709 AND 46301. IN ADDITION, PURSUANT TO 10 U.S.C. SECTION
                130I, 50 U.S.C. SECTION 2661, AND 6 U.S.C. SECTION 124N, THE
                DEPARTMENT OF DEFENSE (DOD), DEPARTMENT OF ENERGY (DOE),
                DEPARTMENT OF HOMELAND SECURITY (DHS), OR DEPARTMENT OF
                JUSTICE (DOJ), RESPECTIVELY , MAY TAKE SECURITY ACTION AT OR
                IN THE VICINITY OF SPECIFIC LOCATIONS PRE-COORDINATED WITH
                THE FAA WITHIN A SUBSET OF THE DEFINED AIRSPACE, OR IN
                RESTRICTED OR PROHIBITED AIRSPACE ADJACENT TO SUCH LOCATIONS,
                THAT RESULTS IN THE INTERFERENCE, DISRUPTION, SEIZURE,
                2009011200-2109011159 END PART 1 OF 4 !FDC 0/5116 FDC PART
                2 OF 4 SECURITY..SPECIAL SECURITY INSTRUCTIONS FOR UNMANNED
                DAMAGING, OR DESTRUCTION OF UNMANNED AIRCRAFT CONSIDER(INCMPL)",
    "start_of_activity_time": "2020-09-01T12:00:00Z",
    "end_of_validity_time": "2021-09-01T11:59:00Z",
    "expiration_time": "2021-06-26T02:24:57Z",
    }

Notes:

* ``"cancel"``: Present only when cancelled. Always check for this first
  and delete the report. No other processing required.

NOTAM-D and NOTAM-FDC
^^^^^^^^^^^^^^^^^^^^^

::

/notam-d
/notam-d/<4 character id>
/notam-fdc
/notam-fdc/<4 character id>

NOTAM-D (distant) and NOTAM-FDC (Flight Data Center)
have identical formats other than 
the subtypes. Both may have geojson 'Point' objects.

These objects (as well as the NOTAM-D-SUA, NOTAM-TMOA and
NOTAM-TRA objects to be described later) will have the following
fields:

* ``"accountable"``: Accountable 
* ``"affected"``: Airport affected.
* ``"keyword"``: Notam type. For non-NOTAM-FDCs, one of:

  * RWY: Runway
  * TWY: Taxiway
  * APRON: Apron/Ramp
  * AD: Aerodrome
  * OBST: Obstruction
  * NAV: Navigation Aid
  * COM: Communications
  * SVC: Services
  * AIRSPACE: Airspace
  * OPD: Obstacle Departure Procedure
  * SID: Standard Instrument Departure
  * STAR: Standard Terminal Arrival

  For NOTAM-FDCs, one of:
  
  * CHART: Chart
  * DATA: Data
  * IAP: Instrument Approach Procedure
  * VFP: Visual Flight Procedures
  * ROUTE: Route
  * SPECIAL: Special
  * SECURITY: Security
  * U: Unverified Aeronautical information
  * O: Other
    
Example NOTAM-D: ::

  {
    "type": "NOTAM",
    "unique_name": "21-12579-KHFY"
    "keyword": "OBST",
    "location": "KHFY",
    "number": "06/579",
    "start_of_activity_time": "2021-06-24T17:47:00Z",
    "accountable": "HUF",
    "affected": "HFY",
    "contents": "!HUF 06/579 HFY OBST TOWER LGT (ASR 1002451)
                 393252.90N0861537.20W (9.3NM WSW HFY) 1042.7FT (294.9FT AGL)
                 U/S 2106241747-2109220400",
    "end_of_validity_time": "2021-09-22T04:00:00Z",
    "expiration_time": "2021-09-22T04:00:00Z",
    "geojson": {
          "features": [
            {
                "geometry": {
                    "coordinates": [-86.087494, 39.626999],
                    "type": "Point"
                },
                "properties": {
                    "airport_id": "KHFY",
                    "altitudes": [0, "AGL", 0, "AGL"],
                    "id": "21-12579-KHFY",
                    "start_time": "2021-06-24T17:47:00Z",
                    "stop_time": "2021-09-22T04:00:00Z"
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    },
  }

Example NOTAM-FDC: ::

  {
    "type": "NOTAM",
    "unique_name": "1-8239"
    "subtype": "FDC",
    "keyword": "IAP",
    "location": "KSBN",
    "number": "1/8239",
    "accountable": "FDC",
    "affected": "SBN",
    "contents": "!FDC 1/8239 SBN IAP SOUTH BEND INTL, SOUTH BEND, IN.\n
                 RNAV (GPS) RWY 9R, AMDT 1A...\nLPV DA NA ALL CATS AND
                 LNAV/VNAV DA NA ALL CATS.\n2106071415-2306071415EST",
    "start_of_activity_time": "2021-06-07T14:15:00Z",
    "end_of_validity_time": "2023-06-07T14:15:00Z",
    "expiration_time": "2023-06-07T14:15:00Z",
  }

Notes:

* ``"cancel"``: Present only when cancelled. Always check for this first
  and delete the report. No other processing required.
* Since airports are located on the ground, the ``"altitudes"`` list will
  always show 0 AGL for hight and low altitudes.
* These NOTAMs will have only 'Point' geojson objects if they have any at all.

NOTAM-D-SUA
^^^^^^^^^^^

::

/notam-d-sua
/notam-d-sua/<4 character ARTCC location>

NOTAM-D SUAs are used to activate special use airspace that, in addition to
regularly active times, also have the provision 'other times by NOTAM'.

Each NOTAM-D SUA will declare an airspace it applies to, and at what altitudes
it is valid for. The start and stop times are also given. 

Most special use airspaces have a single geographical region. But many do not. They
may have up to ten or so geographic
regions that all go under a single name. And each geographic area may
have different times and different altitudes associated with it. But the NOTAM
will only refer to the entire SUA and will only provide one set of altitudes.
To be on the safe side, we assume the NOTAM applies to all geographic portions
and will store the altitudes, but not treat them as the whole truth.

The NOTAM-D SUA never provides a graphic portion, but it is possible to load
the database with SUA graphic information. See the 'fisb-decode' documentation
for more about this.

Also note that while the NOTAM usually indicates a well-known area that is
documented in SUA definition files, the area may not be in the file
(aerial refueling is common), or sometimes they make something up like
'RANDOM AIR REFUELING FKL-THS'.

Fields unique to NOTAM-D SUA:

  * ``"airspace"``: This is the special use airspace official name.
  * ``"altitude_text"``: A text string that defines the altitudes to 
    be used. See the caution about this under the ``"altitudes"`` item
    below.
  * ``"altitudes"``: This is in the exact same form as the altitudes
    field for other objects, but it isn't quite the same. The first
    item is the high altitude, followed by the high altitude type, then
    the low altitude and low altitude type (just like all the other
    ``"altitudes"`` fields).

    However, remember that special use airspaces may have multiple
    geographic areas, each with their own altitudes. We really can't be
    sure how that applies in a given NOTAM-D SUA. That is why, unlike other
    ``"altitudes"`` fields, this one is placed at the top level of the object
    and not inside a ``"geojson"`` field. A good display program would point
    this out when displaying any FAA SUA altitude information.

    Also, it is not clear what altitudes are AGL or MSL. Flight levels are 
    considered MSL, ``SFC`` is considered AGL, but the usual reference is just
    ``'FT'``. If we can't determine AGL or MSL, we are forced to use what
    they tell use, and that is ``'FT'``.

Example: ::

  {
    "type": "NOTAM",
    "unique_name": "21-12582-KZKC"
    "subtype": "D-SUA",
    "keyword": "AIRSPACE",
    "location": "KZKC",
    "number": "06/582",
    "accountable": "SUAC",
    "affected": "ZKC",
    "airspace": "R4501F",
    "altitude_text": "SFC-3200FT",
    "altitudes": [
        3200,
        "FT",
        0,
        "AGL"
    ],
    "start_of_activity_time": "2021-06-25T23:00:00Z",
    "end_of_validity_time": "2021-06-26T05:00:00Z",
    "contents": "!SUAC 06/582 ZKC AIRSPACE R4501F ACT SFC-3200FT 2106252300-2106260500",
    "expiration_time": "2021-06-26T05:00:00Z",
    "geojson": {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        [-92.151396, 37.68334],
                        [-92.181396, 37.68334],
                        [-92.203062, 37.717229],
                        [-92.146118, 37.719451],
                        [-92.151396, 37.68334]
                    ],
                    "type": "Polygon"
                },
                "properties": {
                    "name": "R-4501F",
                    "remarks": "EXCLUDES R-4501A, R-4501B, AND R-4501C WHEN ACTIVE",
                    "times_of_use": "0700 - 1800, DAILY; OTHER TIMES BY NOTAM 24 HOURS IN ADVANCE",
                    "type": "R"
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    },
  }

Notes:

* ``"cancel"``: Present only when cancelled. Always check for this first
  and delete the report. No other processing required.
* If the NOTAM-D SUA has a geojson field, the ``"properties"`` field will contain
  the following fields which are taken from the source data file:

  * ``"name"``: Name of the SUA. Note that the FAA in the NOTAM will taken
    out dashes. This name will contain them. This is probably the better
    display name for users.
  * ``"remarks"``: Remarks taken directly from the data file.
  * ``"times_of_use"``: Times of use taken directly from the data source. This is a
    mix of hard to tell apart local and UTC times.
  * ``"type"``: Single letter code type. ``'R'`` for Restricted, ``'W'`` for Warning,
    ``'A'`` for Alert, etc.
* The ``"accountable"`` field will be (for CONUS) ``SUA`` followed by an ``'E'``,
  ``'C'``, or ``'W'`` for East, Central, or West.
* The ``"location"`` field will be (for CONUS) the three letter code for an ARTCC
  with a 'K' at the front (i.e. ``KZID``).

NOTAM-TMOA, NOTAM-TRA
^^^^^^^^^^^^^^^^^^^^^

::

/notam-tmoa
/notam-tmoa/< 4 letter SUAx location>
/notam-tra
/notam-tra/< 4 letter SUAx location>

These NOTAMs are basically NOTAM-D-SUAs, but the NOTAM itself provides
the geometry.

The location for TMOA and TRA NOTAMs are the SUA sites (SUAE, SUAC, SUAW) as
opposed to D-SUA NOTAMs which use ARTCC site names (KZID, etc).

Example: ::

  <no example available>

Notes:

* ``"cancel"``: Present only when cancelled. Always check for this first
  and delete the report. No other processing required.
* These will not have a top-level ``"altitudes"`` field. The ``"altitudes"``
  field will be inside the geojson object. The only altitude types will be
  AGL and MSL.

FIS-B Unavailable
^^^^^^^^^^^^^^^^^

::

  /fis-b-unavailable
  
Returns FIS-B Unavailable reports. Each report will be in
a separate object. Per the standard, these must be made
available to the pilot. Experience has shown that
most of these are triggered
by some long absence of the actual data, so you will probably
notice the missing data long before FIS-B tells you about it.
It will send these messages for Guam, San Juan, Alaska, and
Hawaii, even if you are in the continental U.S.
  
Example: ::

  {
    "type": "FIS_B_UNAVAILABLE",
    "unique_name": "21-10582"
    "contents": "GUAM NEXRAD PRODUCT UPDATES UNAVAILABLE",
    "expiration_time": "2021-06-25T09:13:59Z",
    "issued_time": "2021-06-22T07:56:00Z",
    "product": "GUAM NEXRAD",
    "centers": [
        "ZAB",
        "ZAU",
        "ZFW",
        "ZHU",
        "ZID",
        "ZKC",
        "ZMP",
        "ZOB"
    ],
  }

Notes:

* ``"product"``: Short coded text description of the unavailable product.
  Will be one of:

  * ALASKA NEXRAD
  * CLOUD TOPS
  * CWA
  * D-NOTAM
  * FDC-NOTAM
  * G-AIRMET
  * GUAM NEXRAD
  * HAWAII NEXRAD
  * ICING
  * LIGHTNING
  * METAR
  * NEXRAD IMAGERY
  * NOTAM-D-CANCEL
  * NOTAM-FDC-CANCEL
  * PIREP ICING
  * PIREP TURBULENCE
  * PIREP URGENT
  * PIREP WIND SHEAR
  * ROUTINE PIREP
  * SAN JUAN NEXRAD
  * SIGMET/CONVECTIVE SIGMET
  * SUA
  * TAF
  * TFR NOTAM
  * TRA-NOTAM/TMOA-NOTAM
  * TURBULENCE
  * WINDS AND TEMPERATURE ALOFT

* ``"centers"``: Locations affected by the outage (don't ask why the
  above centers in the example need to know about Guam NEXRAD).

SUA (replaced by NOTAM-D SUA)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

  /sua

These should no longer be used. They have been functionally
replaced by NOTAM-D SUA. As of 2020 the product range has
been reduced to 5 NM.

Example: ::

  {
    "type": "SUA",
    "unique_name": "21-6934"
    "start_time": "2021-06-25T15:00:00Z",
    "end_time": "2021-06-25T21:00:00Z",
    "schedule_id": "5988401",
    "airspace_id": "23941",
    "status": "P",
    "airspace_type": "B",
    "airspace_name": "AR113(W)",
    "expiration_time": "2021-06-25T21:00:00Z",
    "high_altitude": 23000,
    "low_altitude": 19000,
    "separation_rule": "A",
    "shape_defined": "Y",
  }

Notes:

* Detailed description of fields will not be described, because you
  should not use this. If you desire historical information, a
  good place to look is *Surveillance and Broadcast Services Description
  Document SRT-047 Revision 02* (2013). Revision 01 (2011) also has this information.
  Revision 05 (2020) makes note of the reduced product range and future
  elimination of this product.

xxx
^^^

::


Example: ::

Notes:

xxx
^^^

::


Example: ::

Notes:

xxx
^^^

::


Example: ::

Notes:

xxx
^^^

::


Example: ::

Notes:

xxx
^^^

::


Example: ::

Notes:
