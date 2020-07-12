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


    @classmethod
    def load_votes_into_mysql(cls):
        """Read all json data saved, and push it into mysql db"""
        for dir_name in os.listdir(VOTES_PATH):
            with open(os.path.join(VOTES_PATH, dir_name, JSON_NAME), 'r') as f:
                data = json.load(f)

            c = data['chamber']
            n = data['number']

            entries = db.session.query(Vote.vote_num, Vote.chamber).filter(Vote.vote_num == n).filter(Vote.chamber == c).all()
            if len(entries) > 0:
                # If entry already exists in the database, skip adding it
                continue

            q = data['question']
            d = data['date']
            r = data['result']
            req = data['requires']
            t = data['type']
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
                     required=req,
                     vote_type=t if len(t) <= 32 else t[:32],
                     question=q if len(q) <= 512 else q[:512])

            db.session.add(v)
            db.session.commit()


    @classmethod
    def return_sql_json_by_date(cls, date):
        current_date = date.date()
        date_to_query = current_date
        d = {}

        ordered_dates = db.session.query(Vote.vote_num,
            Vote.question,
            Vote.vote_result,
            Vote.num_yeas,
            Vote.num_nays,
            Vote.num_abstains,
            Vote.date).order_by(Vote.date.desc())

        senate_ordered = ordered_dates.filter(Vote.chamber == 's')
        senate_max_date = senate_ordered.first()[-1].date()
        house_ordered = ordered_dates.filter(Vote.chamber == 'h')
        house_max_date = house_ordered.first()[-1].date()
        
        if current_date > senate_max_date:
            date_to_query = senate_max_date
        d['s'] = senate_ordered.filter(Vote.date >= date_to_query).all()

        if current_date > house_max_date:
            date_to_query = house_max_date
        d['h'] = house_ordered.filter(Vote.date >= date_to_query).all()

        return d

