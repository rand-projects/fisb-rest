from pymongo import MongoClient
from pymongo import errors
from flask import request
from flask import jsonify
from shapely.geometry import Polygon
from shapely.geometry import Point

import fisb_restConfig as cfg
import utilities as util
import dateutil.parser

DEFAULT_LIMIT = 10000
DEFAULT_AFTER = "2004-01-01T00:00:00Z"

# Handle to fisb database. Access elsewhere as util.dbConn
dbConn = None

# Create database connection to mongo
def createDbConn():
    """Connect to database.

    Fails if unable to connect to database.
    """
    global dbConn
    
    client = MongoClient(cfg.MONGO_URI, tz_aware=True)

    # Use the 'fisb' database and possibly location database
    dbConn = client.fisb

def isoStringToDt(isoStr):
    """Convert ISO 8601 string into Datetime object.

    Args:
        isoStr (str): ISO 8601 string (assumed UTC).

    Returns:
        object: Datetime object containing representation
            of supplied ISO 8601 string.
    """
    return dateutil.parser.parse(isoStr)

def dtToIsoString(dt):
    """Change datetime to iso format string ending in Z.

    The standard conversion to an ISO string in UTC appends
    ``+00:00``. We convert the data and then change that to ``Z``.
    
    Args:
        dt (datetime): Datetime object to be converted.

    Returns:
        str: Datetime converted to ISO string.
    """
    return dt.isoformat().replace('+00:00', 'Z')

def convertMsgDtToIsoString(msgDict):
    """Change any '<xxx>_time' entries to ISO string values.
                                                                                                 
    Messages are stored in the database as ``datetime`` objects. For printing
    to files, we convert these back to ISO string values. This
    function takes a message and converts all the slots that end in '_time' into an
    ISO string. These slots are only at the first level, no nesting is performed.
    It will also convert ``start_time`` and ``stop_time`` slots that occur                       
    inside a ``geojson`` slot.                                                               
                                                                                                 
    Args:                                                                                        
        msgDict (dict): Dictionary containing message.

    Returns:
        dict: Dictionary with all time slots changed to ISO strings.
    """
    keys = list(msgDict.keys())

    for k in keys:
        if k.endswith('_time'):
            msgDict[k] = dtToIsoString(msgDict[k])
    
    # Add start_time and stop_time if geometry is present
    if 'geojson' in msgDict:
        geoDict = msgDict['geojson']['features']
        for x in range(0, len(geoDict)):
            if 'start_time' in geoDict[x]['properties']:
                geoDict[x]['properties']['start_time'] = dtToIsoString(geoDict[x]['properties']['start_time'])
            if 'stop_time' in geoDict[x]['properties']:
                geoDict[x]['properties']['stop_time'] = dtToIsoString(geoDict[x]['properties']['stop_time'])
    
    return msgDict

def getStandardQueryItems(request):
    """Given a ``request`` object, parse off any query string parameters
    and return items related to the query strings.

    The following query parameters are allowed:

        * ``limit=``: Maximum number of results to return.
        * ``after=``: Only return any results after the ISO-8601
            timestamp.
        * ``lat=`` and ``lon=``: Returned objects must be polygons and
            have this point inside of them.
        * ``high=`` and ``low=``: Only return results that are in this
            altitude range.

    All query strings are checked for allowed values. Query parameters
    that come in pairs are checked that both exist. Errors will set
    a boolean in the results and include an error string.

    Args:
        request (object): ``request`` object containing query string.

    Returns:
        tuple: Tuple containing:

        1. (bool) ``True`` if any errors were found. Else ``False``.
        2. (str) String with any error message text. If there were no
            errors, this will be an empty string.
        3. (str) ISO-8601 string with the ``after`` parameter. If no
            ``after`` value was specified, will contain the default
            ``after`` value (``'2004-01-01T00:00:00Z'``).
        4. (int) Limit on the number of results to return. If not present,
            the default limit (``10000``) will be returned.
        5. (bool) ``True`` if a latitude and longitude were specified.
                Else ``False``.
        6. (float) Latitude value. ``0.0`` if none specified.
        7. (float) Longitude value. ``0.0`` if none specified.
        8. (bool) ``True`` if high and low altitudes were specified.
               Else ``False``.
        9. (int) High altitude value. ``0`` if no value specified.
        10. (int) Low altitude value. ``0`` if no value specified.
    """
    errorString = ''
    hasError = False

    # 'after' parameter
    after = request.args.get('after')
    if after == None:
        after = DEFAULT_AFTER

    try:
        dt = isoStringToDt(after)
    
    except Exception as _:
        errorString = 'Illegal "after" parameter. '
        after = DEFAULT_AFTER
        hasError = True
    
    # 'limit' parameter
    limit = request.args.get('limit')
    if limit == None:
        limit = DEFAULT_LIMIT

    try:
        limitInt = int(limit)

        if limitInt > DEFAULT_LIMIT:
            limitInt = DEFAULT_LIMIT
        
        if  limitInt < 1:
            raise Exception('')

    except:
        errorString += 'Illegal "limit" parameter.'
        limit = DEFAULT_LIMIT
        hasError = True        

    # 'lat' parameter
    hasLat = False
    latStr = request.args.get('lat')
    latFloat = 0.0

    if latStr != None:
        try:
            latFloat = float(latStr)
            hasLat = True

            if not ((latFloat >= -90.0) and (latFloat <= 90.0)):
                raise Exception('')

        except:    
            errorString += 'Bad latitude parameter. '
            hasError = True        

    # 'long' parameter
    hasLong = False
    longStr = request.args.get('lon')
    longFloat = 0.0

    if longStr != None:
        try:
            longFloat = float(longStr)
            hasLong = True

            if not ((longFloat >= -180.0) and (longFloat <= 180.0)):
                raise Exception('')

        except:    
            errorString += 'Bad longitude parameter. '
            hasError = True        

    hasLatLong = False
    if hasLat or hasLong:
        if hasLat and hasLong:
            hasLatLong = True
        else:
            hasError = True
            errorString += 'Need both lat and long parameters. '

    # 'high' parameter
    hasHigh = False
    highStr = request.args.get('high')
    high = 0

    if highStr != None:
        try:
            high = int(highStr)
            hasHigh = True

            if high < 0:
                raise Exception('')

        except:    
            errorString += 'Bad high parameter. '
            hasError = True        

    # 'low' parameter
    hasLow = False
    lowStr = request.args.get('low')
    low = 0

    if lowStr != None:
        try:
            low = int(lowStr)
            hasLow = True

            if low < 0:
                raise Exception('')

        except:    
            errorString += 'Bad low parameter. '
            hasError = True      

    hasHighLow = False
    if hasHigh or hasLow:
        if hasHigh and hasLow:
            if low > high:
                hasError = True
                errorString += 'Low must be <= high parameter. '
            else:
                hasHighLow = True
        else:
            hasError = True
            errorString += 'Need both high and low parameters. '

    return hasError, errorString.strip(), dt, limitInt, \
        hasLatLong, latFloat, longFloat, hasHighLow, high, low

def addCrlCompleteField(msg):
    """For CRL messages, will check to see if all messages are complete
    and will add the field ``'complete'`` with a value of ``1`` if
    true. If all the messages are not complete, will not alter the message.

    Args:
        msg (object): CRL message to be checked.
    """
    reports = msg['reports']

    if len(reports) == 0:
        msg['complete'] = 1
        return

    if msg['overflow'] == 1:
        msg['complete'] = 0
        return

    for r in reports:
            if '*' not in r:
                msg['complete'] = 0
                return

    msg['complete'] = 1
    return

def augmentRsr(msg):
    """Alters an RSR message to report only percentage received.

    The RSR message that comes from 'fisb-decode' contains a 
    3 element list containing the total number of messages 
    received over an interval, the number of messages per second
    send by that station, and the percentage of possible messages
    received (to the nearest percent). 

    This return alters the message to only return the percentage
    of possible messages received.

    Args:
        msg (object): Message to be checked.
    """
    if 'stations' in msg:
        stations = msg['stations']
        keys = list(stations.keys())
        for k in keys:
            stations[k] = stations[k][2]

def changeStandardFields(msg):
    """Take a 'fisb-decode' message and make altercations
    to remove unneeded fields and other improvements.

    Will do the following:

    * Convert fields ending in ``_time`` to ISO-8601 strings
      from Datetime objects.
    * Remove ``_digest`` and ``_id`` fields from messages.
    * Remove ``station`` field from messages that have an 
      associated CRL (needed internally by harvest to keep
      track of completeness on a per station basis).
    * Alter any CRL message to check for completeness.
    * Alter RSR message to return only percentage received.

    Args:
        msg (object): Message to be checked.
    """
    msg = convertMsgDtToIsoString(msg)

    msgType = msg['type']

    # Remove 'digest' and '_id' from all messages.
    del msg['_id']
    if 'digest' in msg:
        del msg['digest']

    # Remove 'station' from messages which have an associated CRL
    if msgType in ['NOTAM', 'G_AIRMET', 'AIRMET', 'WST', 'CWA', 'SIGMET']:
        if 'station' in msg:
            del msg['station']

    # CRL messages will get a 'complete' field.
    if msgType.startswith('CRL'):
        addCrlCompleteField(msg)
        del msg['product_id']

    # RSR message will get the station value turned into percentage only.
    if msgType == 'RSR':
        augmentRsr(msg)            
    
    return msg

def checkIfInPolygon(msg, lat, lon):
    """Check to see if the given latitude and longitude is
    within a message containing a polygon.

    Note that some messages have multiple polygons.
    Only one needs to fit the requirements to return
    ``True``. 

    Messages that don't contain any geometry, or those that
    contain geometry, but are not polygons, will also return ``True``.
    The basic concept is to err on the side of returning data.
    The especially applies to TWGO messages where the text portion
    of the message may have arrived (and the standard states we need to
    send it), but the graphics portion has not arrived.

    Args:
        msg (object): Message to be checked.
        lat (float): Latitude.
        lon (float): Longitude.

    Returns:
        bool: ``True`` if the message has a polygon and
        the specified point is within that polygon.
        Will also return ``True`` if the message
        doesn't have a polygon. Will only return
        ``False`` if the message has a polygon and
        the specified point is not inside. Note that
        if a message has multiple polygons, all are
        checked. Only one needs to satisfy the 
        requirements.
    """
    if 'geojson' not in msg:
        return True

    point = Point(lon, lat)

    geoList = msg['geojson']['features']
    for x in geoList:
        if x['geometry']['type'] != 'Polygon':
            continue
        coords = x['geometry']['coordinates']
        shapelyCoords = [(xy[0], xy[1]) for xy in coords]

        poly = Polygon(shapelyCoords)
        if not poly.contains(point):
            continue
        return True

    return False

def checkIfInAltBounds(msg, high, low):
    """If the message has geometry and an ``altitudes`` field
    (not including NOTAM-D SUA messages), return ``True`` if
    the altitude range is within the high and low values.

    Messages that don't contain any geometry, or those that
    contain geometry, but don;t have an ``altitudes`` field, will also return ``True``.
    
    Args:
        msg (object): Message to be checked.
        high (float): High altitude value (feet).
        low (float): Low altitude value (feet).

    Returns:
        bool: ``True`` if the message has a geometry
        and an ``altitudes`` field, and there is an 
        match between the high and low parameters and
        the altitudes range.
        Will also return ``True`` if the message
        doesn't have any geometry. Will only return
        ``False`` if the message has a geometry and
        ``altitudes`` fields  and the high and low 
        parameters are not in the range of the
        ``altitudes`` field.
        If a message has multiple geometries, all are
        checked. Only one needs to satisfy the 
        requirements.
    """
    if 'geojson' not in msg:
        return True

    geoList = msg['geojson']['features']
    for x in geoList:
        props = x['properties']
        if 'altitudes' not in props:
            return True

        alts = props['altitudes']
        if (alts[0] == 0) and (alts[0] == alts[2]):
            return True

        # Make sure there is some intersection between the 2 ranges
        if (alts[2] <= high) and (low <= alts[0]):
            return True

        continue

    return False

def returnStaticOne(findArg1, request):
    """Return zero to one message from Mongo collection ``STATIC``.
                                                                                
    Handles all query parameters and error checks.

    This is exactly like the non-static version, but will search 
    the ``STATIC`` rather than the ``MSG`` collection.

    Args:
        findArg1 (dict): Dictionary to be used as the
            first argument to the ``find()`` call to Mongo.
        request (obj): Request object from Flask.

    Returns:
        obj: Message containing zero to one object in the
            ``result`` field.
    """
    result = {}
    
    hasError, errorString, _, _, \
        hasLatLong, lat, lon, \
        hasHighLow, high, low = getStandardQueryItems(request)

    if hasError:
        result['status'] = -1
        result['error'] = errorString
        return jsonify(result)

    msg = dbConn.STATIC.find_one(findArg1)

    if hasLatLong and not checkIfInPolygon(msg, lat, lon):
        msg = None

    if hasHighLow and not checkIfInAltBounds(msg, high, low):
        msg = None

    if msg == None:
        result['status'] = 0
        result['num_results'] = 0
        return jsonify(result)

    del msg['_id']

    result['status'] = 0
    result['result'] = msg
    result['num_results'] = 1
    return jsonify(result)
    
def returnStaticMany(findArg1, request):
    """Return zero to many messages from Mongo collection ``STATIC``.
                                                                                
    Handles all query parameters and error checks.

    This is exactly like the non-static version, but will search 
    the ``STATIC`` rather than the ``MSG`` collection.

    Args:
        findArg1 (dict): Dictionary to be used as the
            first argument to the ``find()`` call to Mongo.
        request (obj): Request object from Flask.

    Returns:
        obj: Message containing zero to many objects in the
            ``results`` field.
    """
    result = {}

    hasError, errorString, _, limit, \
        hasLatLong, lat, lon, \
        hasHighLow, high, low = getStandardQueryItems(request)
    if hasError:
        result['status'] = -1
        result['error'] = errorString
        return jsonify(result)

    cursor = dbConn.STATIC.find(findArg1).limit(limit)
    
    if cursor == None:
        result['status'] = 0
        result['num_results'] = 0
        return jsonify(result)

    numResults = 0
    messages = []

    for msg in cursor:
        if hasLatLong and not checkIfInPolygon(msg, lat, lon):
            continue

        if hasHighLow and not checkIfInAltBounds(msg, high, low):
            continue

        numResults += 1
        del msg['_id']        

        messages.append(msg)

    result['status'] = 0
    result['results'] = messages
    result['num_results'] = numResults
    return jsonify(result)
    
def returnOne(findArg1, request):
    """Return zero or one message from Mongo collection ``MSG``.                            
                                                                                
    Handles all query parameters and error checks.

    Args:
        findArg1 (dict): Dictionary to be used as the
            first argument to the ``find()`` call to Mongo.
        request (obj): Request object from Flask.

    Returns:
        obj: Message containing at most one internal object in the
            ``result`` field.
    """
    result = {}
    
    hasError, errorString, afterDt, _, \
        hasLatLong, lat, lon, \
        hasHighLow, high, low = getStandardQueryItems(request)

    if hasError:
        result['status'] = -1
        result['error'] = errorString
        return jsonify(result)

    findArg1['insert_time'] = {'$gt': afterDt}

    msg = dbConn.MSG.find_one(findArg1)

    if hasLatLong and not checkIfInPolygon(msg, lat, lon):
        msg = None

    if hasHighLow and not checkIfInAltBounds(msg, high, low):
        msg = None

    if msg == None:
        result['status'] = 0
        result['num_results'] = 0
        result['after'] = dtToIsoString(afterDt)
        return jsonify(result)

    msg = changeStandardFields(msg)
    afterStr = msg['insert_time']
    del msg['insert_time']

    result['status'] = 0
    result['result'] = msg
    result['num_results'] = 1
    result['after'] = afterStr
    return jsonify(result)
    
def returnMany(findArg1, request):
    """Return zero to many messages from Mongo collection ``MSG``.                            
                                                                                
    Handles all query parameters and error checks.

    Args:
        findArg1 (dict): Dictionary to be used as the
            first argument to the ``find()`` call to Mongo.
        request (obj): Request object from Flask.

    Returns:
        obj: Message containing at most one internal object in the
            ``results`` field.
    """
    result = {}

    hasError, errorString, afterDt, limit, \
        hasLatLong, lat, lon, \
        hasHighLow, high, low = getStandardQueryItems(request)
    if hasError:
        result['status'] = -1
        result['error'] = errorString
        return jsonify(result)

    findArg1['insert_time'] = {'$gt': afterDt}

    cursor = dbConn.MSG.find(findArg1).sort('insert_time', 1).limit(limit)
    
    if cursor == None:
        result['status'] = 0
        result['num_results'] = 0
        result['after'] = dtToIsoString(afterDt)
        return jsonify(result)

    numResults = 0
    messages = []
    afterStr = dtToIsoString(afterDt)

    for msg in cursor:
        if hasLatLong and not checkIfInPolygon(msg, lat, lon):
            continue

        if hasHighLow and not checkIfInAltBounds(msg, high, low):
            continue

        numResults += 1
        msg = changeStandardFields(msg)

        afterStr = msg['insert_time']
        del msg['insert_time']

        messages.append(msg)

    result['status'] = 0
    result['results'] = messages
    result['num_results'] = numResults
    result['after'] = afterStr
    return jsonify(result)
