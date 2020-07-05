import os
import json
from datetime import datetime

from app import db
from app.models import Vote

CWD = os.path.dirname(os.path.abspath('__file__'))
VOTES_PATH = os.path.join(CWD, '..', '..', 'congress', 'data', '116', 'votes', '2020')
JSON_NAME = 'data.json'


class Votes:
    vote_types = ['s', 'h']
    dv = {}
    dv['s'] = 'Senate'
    dv['h'] = 'House of Representatives'
    dv_dirnames = {}
    dv_date_record = {}
    dv_minmax = {}


    @classmethod
    def load_votes_into_mysql(cls):
        """Read all json data saved, and push it into mysql db"""
        for dir_name in os.listdir(VOTES_PATH):
            with open(os.path.join(VOTES_PATH, dir_name, JSON_NAME), 'r') as f:
                data = json.load(f)

            c = data['chamber']
            n = data['number']
            q = data['question']
            d = data['date']
            r = data['result']
            try:
                nays = data['votes']['Nay']
            except KeyError:
                nays = []
            try:
                yeas = data['votes']['Yea']
            except KeyError:
                yeas = []
            try:
                abstains = data['votes']['Not Voting']
            except KeyError:
                abstains = []

            d = d[:19] # strip off the timezone offset
            dt = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S').date()

            num_nays = len(nays)
            num_yeas = len(yeas)
            num_abstains = len(abstains)

            v = Vote(chamber=c,
                     vote_num=n,
                     date=dt,
                     vote_result=r if len(r) <= 64 else r[:64],
                     num_yeas=num_yeas,
                     num_nays=num_nays,
                     num_abstains=num_abstains,
                     question=q if len(q) <= 512 else q[:512])

            db.session.add(v)
            db.session.commit()


    @classmethod
    def return_sql_json_by_date(cls, date):
        start = date.date()
        d = {}

        d['s'] = db.session.query(Vote.vote_num,
            Vote.question,
            Vote.vote_result,
            Vote.num_yeas,
            Vote.num_nays,
            Vote.num_abstains,
            Vote.date).filter(Vote.date >= start).filter(Vote.chamber == 's').order_by(Vote.date).all()

        d['h'] = db.session.query(Vote.vote_num,
            Vote.question,
            Vote.vote_result,
            Vote.num_yeas,
            Vote.num_nays,
            Vote.num_abstains,
            Vote.date).filter(Vote.date >= start).filter(Vote.chamber == 'h').order_by(Vote.date).all()

        return d


    @classmethod
    def loadsort_new_votes(cls):
        """dirnames dictionary. Sets the minimum and maximum seen
        vote ID for each type of vote"""
        for v in cls.vote_types:
            cls.dv_dirnames[v] = sorted([x for x in os.listdir(VOTES_PATH) if x.startswith(v)], key=lambda x: int(x[len(v):]))
            cls.dv_minmax[v] = {}
            cls.dv_minmax[v]['min'] = cls.dv_dirnames[v][0]
            cls.dv_minmax[v]['max'] = cls.dv_dirnames[v][-1]


    @classmethod
    def process_all_records_date(cls):
        """For both senate and house votes, construct a dictionary with keys
        as the dates of the session, and values as a list of votes that occured on that date.
        If no votes occured on a date, that date will not be included in dictionary."""
        for v in cls.vote_types:
            cls.dv_date_record[v] = {} # initialize the 1-layer deep nested dictionary
            for dirname in cls.dv_dirnames[v][::-1]:
                with open(os.path.join(VOTES_PATH, dirname, JSON_NAME), 'r') as f:
                    data = json.load(f)
                date = data['date']
                date = date[:19] # strip off the timezone offset
                dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').date()
                try:
                    cls.dv_date_record[v][str(dt)].append(dirname)
                except KeyError:
                    cls.dv_date_record[v][str(dt)] = [dirname]

            sorted_dates = sorted(cls.dv_date_record[v].keys())
            cls.dv_minmax[v]['maxdate'] = sorted_dates[-1]
            cls.dv_minmax[v]['mindate'] = sorted_dates[0]


    @classmethod
    def return_json_by_date(cls, date):
        d = {}
        for v in cls.vote_types:
            # iterate over all vote types
            d[v] = []
            try:
                # try to get the date in dictionary
                v_ids = cls.dv_date_record[v][str(date)]
                for ids in v_ids:
                    # iterate over all vote ids that occured on that date
                    with open(os.path.join(VOTES_PATH, ids, JSON_NAME), 'r') as f:
                        j = json.load(f)
                        d[v].append(j)
            except KeyError:
                # date not in dictionary
                if str(date) > cls.dv_minmax[v]['maxdate']:
                    v_ids = cls.dv_date_record[v][cls.dv_minmax[v]['maxdate']]
                    for ids in v_ids:
                        # iterate over all vote ids that occured on that date
                        with open(os.path.join(VOTES_PATH, ids, JSON_NAME), 'r') as f:
                            j = json.load(f)
                            d[v].append(j)
                elif str(date) < cls.dv_minmax[v]['mindate']:
                    v_ids = cls.dv_date_record[v][cls.dv_minmax[v]['mindate']]
                    for ids in v_ids:
                        # iterate over all vote ids that occured on that date
                        with open(os.path.join(VOTES_PATH, ids, JSON_NAME), 'r') as f:
                            j = json.load(f)
                            d[v].append(j)
        return d


