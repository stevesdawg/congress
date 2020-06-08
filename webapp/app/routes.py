import os
import json
import requests
import datetime
from flask import render_template
from Votes import Votes
from app import app

# globals
CWD = os.path.dirname(os.path.abspath('__file__'))
BILLS_PATH = os.path.join(CWD, '..', '..', 'congress', 'data', '116', 'bills')
JSON_NAME = 'data.json'


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

# filenames dictionary
d_filenames = {}
for b in bill_types:
    d_filenames[b] = sorted(os.listdir(os.path.join(BILLS_PATH, b)), key=lambda x: int(x[len(b):]))

# latest directory dictionary
d_latest = {}
for b in bill_types:
    d_latest[b] = os.path.join(BILLS_PATH, b, d_filenames[b][-1])

# latest json data dictionary
d_latest_data = {}
for b in bill_types:
    with open(os.path.join(d_latest[b], JSON_NAME), 'r') as f:
        data = json.load(f)
    d_latest_data[b] = data

# latest bills text dictionary
d_latest_urls = {}
for b in bill_types:
    url = "https://api.fdsys.gov/link?collection=bills&billtype=" + b + "&billnum=" + d_latest_data[b]['number'] + "&congress=" + d_latest_data[b]['congress']
    r = requests.get(url, timeout=1)
    if r.status_code >= 400:
        d_latest_urls[b] = None
    else:
        d_latest_urls[b] = url

Votes.loadsort_new_votes()
Votes.process_all_records_date()
latest_votes = Votes.return_json_by_date(str(datetime.datetime.now().date()))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index_votes.html', vote_types=Votes.vote_types, dv=Votes.dv,
        dv_latest_data=latest_votes, bill_types=bill_types, d=d,
        d_latest_data=d_latest_data, d_latest_urls=d_latest_urls)
