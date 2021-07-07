from flask import Flask
from flask import request
from flask import jsonify

import fisb_restConfig as cfg
import utilities as util

app = Flask(__name__, static_url_path='')

# Create database connection to mongo
util.createDbConn()

@app.route("/")
def root():
    """Root web page. Shows ``static/index.html``.

    Returns:
        str: ``static/index.html`` web page.
    """
    return app.send_static_file('index.html')

@app.route("/all")
def all():
    """Sends all documents.

    Returns:
        str: JSON response.
    """
    return util.returnMany({}, request)

@app.route("/metar")
def metar():
    """Sends all METARs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'METAR'}, request)

@app.route("/metar/<id>")
def metar_id(id):
    """Sends specific METAR.

    Args:
        id (str): 4 character ICAO METAR to send.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'METAR', 'unique_name': id.upper()}, request)

@app.route("/taf")
def taf():
    """Sends all TAFs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'TAF'}, request)

@app.route("/taf/<id>")
def taf_id(id):
    """Sends specific TAF.

    Args:
        id (str): 4 character ICAO TAF to send.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'TAF', 'unique_name': id.upper()}, request)

@app.route("/pirep")
def pirep():
    """Sends all PIREPS.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'PIREP'}, request)

@app.route("/wind-06")
def wind06():
    """Sends all 06 hour wind forecasts.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'WINDS_06_HR'}, request)

@app.route("/wind-06/<id>")
def wind06_id(id):
    """Sends specific 06 hour wind forecast.

    Args:
        id (str): 3 character id of station.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'WINDS_06_HR', 'unique_name': id.upper()}, request)

@app.route("/wind-12")
def wind12():
    """Sends all 12 hour wind forecasts.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'WINDS_12_HR'}, request)

@app.route("/wind-12/<id>")
def wind12_id(id):
    """Sends specific 12 hour wind forecast.

    Args:
        id (str): 3 character id of station.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'WINDS_12_HR', 'unique_name': id.upper()}, request)

@app.route("/wind-24")
def wind24():
    """Sends all 24 hour wind forecasts.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'WINDS_24_HR'}, request)

@app.route("/wind-24/<id>")
def wind24_id(id):
    """Sends specific 24 hour wind forecast.

    Args:
        id (str): 3 character id of station.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'WINDS_24_HR', 'unique_name': id.upper()}, request)

@app.route("/sigmet")
def sigmet():
    """Sends all SIGMETs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'SIGMET'}, request)

@app.route("/airmet")
def airmet():
    """Sends all AIRMETs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'AIRMET'}, request)

@app.route("/cwa")
def cwa():
    """Sends all CWAs (Center Weather Advisories).

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CWA'}, request)

@app.route("/rsr")
def rsr():
    """Sends Reception Success Rate (RSR) object.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'RSR'}, request)

@app.route("/service-status")
def service_status():
    """Sends current Service Status object.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'SERVICE_STATUS'}, request)

@app.route("/g-airmet")
def g_airmet():
    """Sends all G-AIRMETs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'G_AIRMET'}, request)

@app.route("/g-airmet-00")
def g_airmet00():
    """Sends all 00 hour G-AIRMETs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'G_AIRMET', 'subtype': 0}, request)

@app.route("/g-airmet-03")
def g_airmet03():
    """Sends all 03 hour G-AIRMETs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'G_AIRMET', 'subtype': 3}, request)

@app.route("/g-airmet-06")
def g_airmet06():
    """Sends all 06 hour G-AIRMETs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'G_AIRMET', 'subtype': 6}, request)

@app.route("/fis-b-unavailable")
def fisb_unavailable():
    """Sends all FIS-B Unavailable objects.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'FIS_B_UNAVAILABLE'}, request)

@app.route("/notam-tfr")
def notam_tfr():
    """Sends all NOTAM-TFRs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'TFR'}, request)

@app.route("/notam")
def notam():
    """Sends all NOTAMs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM'}, request)

@app.route("/notam/<id>")
def notam_id(id):
    """Sends all NOTAMs for specific location.

    Args:
        id (str): 4 character ICAO METAR to send.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'location': id.upper()}, request)

@app.route("/notam-d")
def notam_d():
    """Sends all NOTAM-Ds.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'D'}, request)

@app.route("/notam-d/<id>")
def notam_d_id(id):
    """Sends all NOTAM-Ds for specific location.

    Args:
        id (str): 4 character ICAO METAR to send.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'D', 'location': id.upper()}, request)

@app.route("/notam-d-sua")
def notam_d_sua():
    """Sends all NOTAM-D SUAs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'D-SUA'}, request)

@app.route("/notam-d-sua/<id>")
def notam_d_sua_id(id):
    """Sends all NOTAM-D SUAs for specific location.

    Args:
        id (str): 4 character ICAO METAR to send.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'D-SUA', 'location': id.upper()}, request)

@app.route("/notam-fdc")
def notam_fdc():
    """Sends all NOTAM-FDCs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'FDC'}, request)

@app.route("/notam-fdc/<id>")
def notam_fdc_id(id):
    """Sends all NOTAM-D FDCs for specific location.

    Args:
        id (str): 4 character ICAO METAR to send.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'FDC', 'location': id.upper()}, request)

@app.route("/notam-tmoa")
def notam_tmoa():
    """Sends all NOTAM-TMOAs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'TMOA'}, request)

@app.route("/notam-tmoa/<id>")
def notam_tmoa_id(id):
    """Sends all NOTAM TMOAs for specific location.

    Args:
        id (str): 4 character ICAO METAR to send.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'TMOA', 'location': id.upper()}, request)

@app.route("/notam-tra")
def notam_tra():
    """Sends all NOTAM-TRAs.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'TRA'}, request)

@app.route("/notam-tra/<id>")
def notam_tra_id(id):
    """Sends all NOTAM TRAs for specific location.

    Args:
        id (str): 4 character ICAO METAR to send.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'subtype': 'TRA', 'location': id.upper()}, request)

@app.route("/cancel-notam")
def notam_cancel():
    """Sends an object for each cancelled NOTAM.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'NOTAM', 'cancel': {'$exists': True}}, request)

@app.route("/cancel-g-airmet")
def g_airmet_cancel():
    """Sends an object for each cancelled G-AIRMET.    

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'G_AIRMET', 'cancel': {'$exists': True}}, request)

@app.route("/cancel-cwa")
def cwa_cancel():
    """Sends an object for each cancelled CWA.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CWA', 'cancel': {'$exists': True}}, request)

@app.route("/cancel-sigmet")
def sigmet_cancel():
    """Sends an object for each cancelled SIGMET.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'SIGMET', 'cancel': {'$exists': True}}, request)

@app.route("/cancel-airmet")
def airmet_cancel():
    """Sends an object for each cancelled AIRMET.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'AIRMET', 'cancel': {'$exists': True}}, request)

@app.route("/cancel")
def cancel():
    """Sends an object for each type of cancelled message of any type.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': {'$in': ['AIRMET', 'SIGMET', 'CWA', \
        'G_AIRMET', 'NOTAM']}, 'cancel': {'$exists': True}}, request)

@app.route("/crl-notam-tfr")
def crl_notam_tfr():
    """Sends all CRL-NOTAM-TFRs (CRL-8).

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CRL_8'}, request)

@app.route("/crl-notam-tfr/<id>")
def crl_notam_tfr_id(id):
    """Send CRL-NOTAM-TFR object for a particular station (CRL-8).

    Args:
        id (str): Station name to retreive.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'CRL_8', 'station': id}, request)

@app.route("/crl-airmet")
def crl_airmet():
    """Sends all CRL-AIRMET objects (CRL-11).

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CRL_11'}, request)

@app.route("/crl-airmet/<id>")
def crl_airmet_id(id):
    """Send CRL-AIRMET object for a particular station (CRL-11).

    Args:
        id (str): Station name to retreive.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'CRL_11', 'station': id}, request)

@app.route("/crl-sigmet")
def crl_sigmet():
    """Sends all CRL-SIGMET objects (CRL-12).

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CRL_12'}, request)

@app.route("/crl-sigmet/<id>")
def crl_sigmet_id(id):
    """Send CRL-SIGMET object for a particular station (CRL-12).

    Args:
        id (str): Station name to retreive.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'CRL_12', 'station': id}, request)

@app.route("/crl-g-airmet")
def crl_g_airmet():
    """Sends all CRL-G-AIRMET objects (CRL-14).

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CRL_14'}, request)

@app.route("/crl-g-airmet/<id>")
def crl_g_airmet_id(id):
    """Send CRL-G-AIRMET object for a particular station (CRL-14).

    Args:
        id (str): Station name to retreive.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'CRL_14', 'station': id}, request)

@app.route("/crl-cwa")
def crl_cwa():
    """Sends all CRL-CWA objects (CRL-15).

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CRL_15'}, request)

@app.route("/crl-cwa/<id>")
def crl_cwa_id(id):
    """Send CRL-CWA object for a particular station (CRL-15).

    Args:
        id (str): Station name to retreive.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'CRL_15', 'station': id}, request)

@app.route("/crl-notam-tra")
def crl_notam_tra():
    """Sends all CRL-NOTAM-TRA objects (CRL-16).

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CRL_16'}, request)

@app.route("/crl-notam-tra/<id>")
def crl_notam_tra_id(id):
    """Send CRL-NOTAM-TRA object for a particular station (CRL-16).

    Args:
        id (str): Station name to retreive.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'CRL_16', 'station': id}, request)

@app.route("/crl-notam-tmoa")
def crl_notam_tmoa():
    """Sends all CRL-NOTAM-TMOA objects (CRL-17).

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'CRL_17'}, request)

@app.route("/crl-notam-tmoa/<id>")
def crl_notam_tmoa_id(id):
    """Send CRL-NOTAM-TMOA object for a particular station (CRL-17).

    Args:
        id (str): Station name to retreive.

    Returns:
        str: JSON response.
    """
    return util.returnOne({'type': 'CRL_17', 'station': id}, request)

@app.route("/sua")
def sua():
    """Sends all SUA (Special Use Airpace) objects.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'SUA'}, request)

@app.route("/image")
def image():
    """Sends all image objects.

    Returns:
        str: JSON response.
    """
    return util.returnMany({'type': 'IMAGE'}, request)

@app.route("/image/<id>")
def imageId(id):
    """Send information about a particular image.

    Args:
        id (str): Image to use. Image name is one of:

            * ``NEXRAD-REGIONAL``
            * ``NEXRAD-CONUS``
            * ``CLOUD-TOPS``
            * ``LIGHTNING``
            * ``ICING-02000`` through ``ICING-24000``
            * ``TURBULENCE-02000`` through ``TURBULENCE-24000``

    Returns:
        str: JSON response.
    """
    id = id.replace('-','_')
    return util.returnOne({'type': 'IMAGE', 'unique_name': id}, request)

@app.route("/static/legend")
def staticLegend():
    """Sends object contain colors and legend information for images.

    Returns:
        str: JSON response.
    """
    return util.returnStaticOne({'_id': 'LEGEND'}, request)
