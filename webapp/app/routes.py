import os
import json
import requests
import datetime
from flask import render_template, jsonify, request
from app.Votes import Votes
from app import Budget
from app import app

# globals
CWD = os.path.dirname(os.path.abspath('__file__'))
BILLS_PATH = os.path.join(CWD, '..', '..', 'congress', 'data', '116', 'bills')
JSON_NAME = 'data.json'

DEBUG = False

# BILLS SCRAPER
d = {}
bill_types = ['hconres', 'hjres', 'hr', 'hres', 's', 'sres', 'sconres', 'sjres']
d['hconres'] = 'House Concurrent Resolution'
d['hjres'] = 'House Joint Resolution'
d['hr'] = 'House of Representatives'
d['hres'] = 'House Simple Resolution'
d['s'] = 'Senate'
d['sres'] = 'Senate Simple Resolution'
d['sconres'] = 'Senate Concurrent Resolution'
d['sjres'] = 'Senate Joint Resolution'

d_filenames = {}
d_latest = {}
d_latest_data = {}
d_latest_urls = {}
# filenames dictionary
for b in bill_types:
    # sort by bill-number. Bill number is the suffix of the filename.
    # Use lambda to sort by the suffix.
    d_filenames[b] = sorted(os.listdir(os.path.join(BILLS_PATH, b)), key=lambda x: int(x[len(b):]))

# latest directory dictionary
for b in bill_types:
    d_latest[b] = os.path.join(BILLS_PATH, b, d_filenames[b][-1])

# latest json data dictionary
for b in bill_types:
    with open(os.path.join(d_latest[b], JSON_NAME), 'r') as f:
        data = json.load(f)
    d_latest_data[b] = data

if not DEBUG:
    # latest bills text dictionary
    for b in bill_types:
        url = "https://api.fdsys.gov/link?collection=bills&billtype=" + b + "&billnum=" + d_latest_data[b]['number'] + "&congress=" + d_latest_data[b]['congress']
        try:
            r = requests.get(url, timeout=1)
            if r.status_code >= 400:
                d_latest_urls[b] = None
            else:
                d_latest_urls[b] = url
        except requests.ReadTimeout:
            d_latest_urls[b] = None


@app.route('/budget_data')
def transmit_data():
    if request.args['id'] == '1':
        return jsonify(Budget.read_mysql_deficit_surplus())
    elif request.args['id'] == '2':
        return jsonify(Budget.read_mysql_receipt_breakdown())
    elif request.args['id'] == '3':
        return jsonify(Budget.read_mysql_outlay_breakdown())


@app.route('/budget')
def budget():
    return render_template('data.html')

@app.route('/')
@app.route('/index')
def index():
    latest_votes = Votes.return_sql_json_by_date(datetime.datetime.now() - datetime.timedelta(5, 0, 0))

    return render_template('index_votes.html', vote_types=Votes.vote_types, dv=Votes.dv,
        dv_latest_data=latest_votes, bill_types=bill_types, d=d,
        d_latest_data=d_latest_data, d_latest_urls=d_latest_urls)
