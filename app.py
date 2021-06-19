from flask import Flask
from flask import request
from flask import jsonify

import fisb_restConfig as cfg
import utilities as util

app = Flask(__name__)

# Create database connection to mongo
util.createDbConn()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/all")
def all():
    return util.returnMany({}, request)

@app.route("/metar")
def metar():
    return util.returnMany({'type': 'METAR'}, request)

@app.route("/metar/<id>")
def metars(id):
    return util.returnOne({'type': 'METAR', 'unique_name': id.upper()}, request)

@app.route("/taf")
def tafs():
    return util.returnMany({'type': 'TAF'}, request)

@app.route("/taf/<id>")
def taf(id):
    return util.returnOne({'type': 'TAF', 'unique_name': id.upper()}, request)

@app.route("/pirep")
def pireps():
    return util.returnMany({'type': 'PIREP'}, request)

@app.route("/wind-06")
def winds06():
    return util.returnMany({'type': 'WINDS_06_HR'}, request)

@app.route("/wind-06/<id>")
def wind06(id):
    return util.returnOne({'type': 'WINDS_06_HR', 'unique_name': id.upper()}, request)

@app.route("/wind-12")
def winds12():
    return util.returnMany({'type': 'WINDS_12_HR'}, request)

@app.route("/wind-12/<id>")
def wind012(id):
    return util.returnOne({'type': 'WINDS_12_HR', 'unique_name': id.upper()}, request)

@app.route("/wind-24")
def winds24():
    return util.returnMany({'type': 'WINDS_24_HR'}, request)

@app.route("/wind-24/<id>")
def wind24(id):
    return util.returnOne({'type': 'WINDS_24_HR', 'unique_name': id.upper()}, request)

@app.route("/sigmet")
def sigmet():
    return util.returnMany({'type': 'SIGMET'}, request)

@app.route("/airmet")
def airmet():
    return util.returnMany({'type': 'AIRMET'}, request)

@app.route("/wst")
def wst():
    return util.returnMany({'type': 'WST'}, request)

@app.route("/cwa")
def cwa():
    return util.returnMany({'type': 'CWA'}, request)

@app.route("/rsr")
def rsr():
    return util.returnOne({'type': 'RSR'}, request)

@app.route("/service-status")
def service_status():
    return util.returnMany({'type': 'SERVICE_STATUS'}, request)

@app.route("/g-airmet")
def g_airmet():
    return util.returnMany({'type': 'G_AIRMET'}, request)

@app.route("/g-airmet-00")
def g_airmet00():
    return util.returnMany({'type': 'G_AIRMET', 'subtype': 0}, request)

@app.route("/g-airmet-03")
def g_airmet03():
    return util.returnMany({'type': 'G_AIRMET', 'subtype': 3}, request)

@app.route("/g-airmet-06")
def g_airmet06():
    return util.returnMany({'type': 'G_AIRMET', 'subtype': 6}, request)

@app.route("/fis-b-unavailable")
def fisb_unavailable():
    return util.returnMany({'type': 'FIS_B_UNAVAILABLE'}, request)

@app.route("/notam-tfr")
def notam_tfr():
    return util.returnMany({'type': 'NOTAM', 'subtype': 'TFR'}, request)

@app.route("/notam")
def notam():
    return util.returnMany({'type': 'NOTAM'}, request)

@app.route("/notam/<id>")
def notam_id(id):
    return util.returnMany({'type': 'NOTAM', 'location': id.upper()}, request)

@app.route("/notam-d")
def notam_d():
    return util.returnMany({'type': 'NOTAM', 'subtype': 'D'}, request)

@app.route("/notam-d/<id>")
def notam_d_id(id):
    return util.returnMany({'type': 'NOTAM', 'subtype': 'D', 'location': id.upper()}, request)

@app.route("/notam-d-sua")
def notam_d_sua():
    return util.returnMany({'type': 'NOTAM', 'subtype': 'D-SUA'}, request)

@app.route("/notam-d-sua/<id>")
def notam_d_sua_id(id):
    return util.returnMany({'type': 'NOTAM', 'subtype': 'D-SUA', 'location': id.upper()}, request)

@app.route("/notam-fdc")
def notam_fdc():
    return util.returnMany({'type': 'NOTAM', 'subtype': 'FDC'}, request)

@app.route("/notam-fdc/<id>")
def notam_fdc_id(id):
    return util.returnMany({'type': 'NOTAM', 'subtype': 'FDC', 'location': id.upper()}, request)

@app.route("/notam-tmoa")
def notam_tmoa():
    return util.returnMany({'type': 'NOTAM', 'subtype': 'TMOA'}, request)

@app.route("/notam-tra")
def notam_tra():
    return util.returnMany({'type': 'NOTAM', 'subtype': 'TRA'}, request)

@app.route("/crl-8")
def crl_8():
    return util.returnMany({'type': 'CRL_8'}, request)

@app.route("/crl-11")
def crl_11():
    return util.returnMany({'type': 'CRL_11'}, request)

@app.route("/crl-12")
def crl_12():
    return util.returnMany({'type': 'CRL_12'}, request)

@app.route("/crl-14")
def crl_14():
    return util.returnMany({'type': 'CRL_14'}, request)

@app.route("/crl-15")
def crl_15():
    return util.returnMany({'type': 'CRL_15'}, request)

@app.route("/crl-16")
def crl_16():
    return util.returnMany({'type': 'CRL_16'}, request)

@app.route("/crl-17")
def crl_17():
    return util.returnMany({'type': 'CRL_17'}, request)

@app.route("/sua")
def sua():
    return util.returnMany({'type': 'SUA'}, request)

@app.route("/image")
def image():
    return util.returnMany({'type': 'IMAGE'}, request)

@app.route("/image/<id>")
def imageId(id):
    id = id.replace('-','_')
    return util.returnMany({'type': 'IMAGE', 'unique_name': id}, request)
