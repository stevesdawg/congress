import os
import json
from datetime import datetime
import xml.etree.cElementTree as ET
from sqlalchemy import func

from app import db
from app.models import Vote, Bill, BillType, Representative, LegislativeSubjects, BillStatus

CWD = os.path.dirname(os.path.abspath('__file__'))
BILLS_PATH = os.path.join(CWD, '..', '..', 'congress', 'data', '116', 'bills')
XML_FILE = 'fdsys_billstatus.xml'
JSON_FILE = 'data.json'
LAST_MOD_FILE1 = 'data-fromfdsys-lastmod.txt'
LAST_MOD_FILE2 = 'fdsys_billstatus-lastmod.txt'

class Bills:
    @classmethod
    def load_bills_into_mysql(cls, last_mod_flag=False):
        """Read all json bill data, and push it into mysql db.
           Link table with other tables (Votes, Reps, Status, Subjects, etc.)"""
        # Today's Date
        today = datetime.now().date()

        for bill_type in BillType.types:
            db_bill_type = getattr(BillType, bill_type.upper())
            type_path = os.path.join(BILLS_PATH, bill_type)

            for dir_name in os.listdir(type_path):
                if last_mod_flag:
                    # check from one of the two last-modified files
                    try:
                        with open(os.path.join(type_path, dir_name, LAST_MOD_FILE1), 'r') as f:
                            last_mod = f.read()
                    except IOError:
                        with open(os.path.join(type_path, dir_name, LAST_MOD_FILE2), 'r') as f:
                            last_mod = f.read()
                    last_mod = last_mod[:10]
                    last_mod = datetime.strptime(last_mod, '%Y-%m-%d').date()
                    if (today - last_mod).days > 0:
                        # if last modified is greater than 1 day,
                        # then ignore that file, and continue
                        continue

                with open(os.path.join(type_path, dir_name, JSON_FILE), 'r') as f:
                    data = json.load(f)

                if data['short_title'] == None:
                    if data['popular_title'] == None:
                        title = data['official_title']
                    else:
                        title = data['popular_title']
                else:
                    title = data['short_title']
                title = title if len(title) <= 256 else title[:256]

                cong = data['congress']
                num = data['number']
                active = data['history']['active']
                sig = data['history']['awaiting_signature']
                enact = data['history']['enacted']
                veto = data['history']['vetoed']
                try:
                    comm = data['committees'][0]['committee']
                except IndexError:
                    comm = None

                intro_date = data['introduced_at']
                intro_date = datetime.strptime(intro_date, '%Y-%m-%d').date()

                bill_q = db.session.query(Bill) \
                    .filter(Bill.bill_type == db_bill_type) \
                    .filter(Bill.bill_num == num) \
                    .filter(Bill.congress == cong)
                bills = bill_q.all()

                if len(bills) > 0:
                    # if the bill has been instantiated,
                    # check if bill has been fully populated
                    b = bills[0]
                    populated = b.title
                    if not populated:
                        # if not populated, instantiate key identifying info (title, origin date)
                        b.congress = cong
                        b.title = title
                        b.introduced_date = intro_date
                    # overwrite with most recent status info
                    b.active = active
                    b.awaiting_sig = sig
                    b.enacted = enact
                    b.vetoed = veto
                    b.committee = comm
                else:
                    # if bill has NOT been instantiated,
                    # create instantiation and add to db
                    b = Bill(title=title,
                        congress=cong,
                        bill_type=db_bill_type,
                        bill_num=num,
                        introduced_date=intro_date,
                        committee=comm,
                        active=active,
                        awaiting_sig=sig,
                        enacted=enact,
                        vetoed=veto)
                    db.session.add(b)

                # bill statuses and actions
                actions = data['actions']
                for act in actions:
                    stat = BillStatus()
                    d = act['acted_at'][:10]
                    d = datetime.strptime(d, '%Y-%m-%d').date()
                    text = act['text']
                    text = text if len(text) < 128 else text[:128]
                    act_type = act['type']
                    stat.date = d
                    stat.text = text
                    stat.action_type = act_type
                    b.statuses.append(stat)

                # legislative subjects
                subjects = data['subjects']
                for subj in subjects:
                    subj_q = LegislativeSubjects.query.filter(func.lower(LegislativeSubjects.subject) == subj.lower())
                    loaded_subjects = subj_q.all()
                    if loaded_subjects:
                        for sub in loaded_subjects:
                            b.leg_subjects.append(sub)
                    else:
                        new_sub = LegislativeSubjects()
                        new_sub.subject = subj
                        b.leg_subjects.append(new_sub)

                # data variable reassigned FROM json TO XML tree
                data = ET.parse(os.path.join(type_path, dir_name, XML_FILE)).getroot()

                # sponsors
                spon = data[0].findall('sponsors')
                spon = spon[0]
                bio_id = spon[0].find('bioguideId').text
                lname = spon[0].find('lastName').text
                fname = spon[0].find('firstName').text
                state = spon[0].find('state').text
                party = spon[0].find('party').text

                if db_bill_type < 5:
                    # Bill originated in the House of Representatives
                    # Search for reps using bioguide_id
                    rep_q = Representative.query.filter(Representative.bioguide_id == bio_id)
                else:
                    # Bill originated in the Senate
                    # Search for reps using state + party lastname
                    rep_q = Representative.query.filter(Representative.state == state) \
                        .filter(Representative.party == party) \
                        .filter(func.lower(Representative.lname) == lname.lower())
                reps = rep_q.all()

                if len(reps) > 0:
                    # representative exists in the database
                    # add them as a sponsor to this bill.
                    rep = reps[0]
                else:
                    rep = Representative()
                rep.bioguide_id = bio_id
                rep.fname = fname
                rep.lname = lname
                mname = spon[0].find('middleName').text
                if mname is not None:
                    rep.mname = mname
                rep.state = state
                rep.party = party
                rep.active = True
                b.sponsor = rep

                # cosponsors
                cospon = data[0].findall('cosponsors')
                cospon = cospon[0]
                for c in cospon:
                    bio_id = c.find('bioguideId').text
                    lname = c.find('lastName').text
                    fname = c.find('firstName').text
                    state = c.find('state').text
                    party = c.find('party').text

                    if db_bill_type < 5:
                        # Bill originated in the House of Representatives
                        # Search for reps using bioguide_id
                        rep_q = Representative.query.filter(Representative.bioguide_id == bio_id)
                    else:
                        # Bill originated in the Senate
                        # Search for reps using state + party lastname
                        rep_q = Representative.query.filter(Representative.state == state) \
                            .filter(Representative.party == party) \
                            .filter(func.lower(Representative.lname) == lname.lower())
                    reps = rep_q.all()
                    if len(reps) > 0:
                        # representative exists in the database
                        # add them as a cosponsor to this bill.
                        rep = reps[0]
                    else:
                        rep = Representative()
                    rep.bioguide_id = bio_id
                    rep.fname = fname
                    rep.lname = lname
                    mname = c.find('middleName').text
                    if mname is not None:
                        rep.mname = mname
                    rep.state = state
                    rep.party = party
                    rep.active = True
                    b.cosponsors.append(rep)

                db.session.commit()

