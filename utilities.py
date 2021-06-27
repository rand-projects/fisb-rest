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
    global dbConn
    
    client = MongoClient(cfg.MONGO_URI, tz_aware=True)

    # Use the 'fisb' database and possibly location database
    dbConn = client.fisb

def isoStringToDt(isoStr):
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

    return hasError, errorString, dt, limitInt, \
        hasLatLong, latFloat, longFloat, hasHighLow, high, low

def addCrlCompleteField(msg):
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
    if 'stations' in msg:
        stations = msg['stations']
        keys = list(stations.keys())
        for k in keys:
            stations[k] = stations[k][2]

def changeStandardFields(msg):
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

def checkIfInPolygon(msg, lat, long):
    if 'geojson' not in msg:
        return True

    point = Point(long, lat)

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

def returnStaticOne(findArg1, request, delFields=[]):
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
    
def returnStaticMany(findArg1, request, delFields=[]):
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
