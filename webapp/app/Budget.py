import os
import pandas as pd
import numpy as np

from app import db
from app.models import DeficitSurplus

# globals
CWD = os.path.dirname(os.path.abspath('__file__'))
EXCEL_DIR = os.path.join(CWD, '..', 'data', 'hist_fy21')
BUDGET_1 = 'hist01z1.xlsx'
EXCEL_FILES = sorted(os.listdir(EXCEL_DIR))
BUDGET_ROW_THRESH = 6


def read_mysql_deficit_surplus():
    data_dict = {}
    tot_data_query = db.session.query(DeficitSurplus.year).order_by(DeficitSurplus.year)
    data_dict['years'] = [x[0] for x in tot_data_query.all()]
    tot_data_query = db.session.query(DeficitSurplus.total_receipt).order_by(DeficitSurplus.year)
    data_dict['total_receipts'] = [x[0] for x in tot_data_query.all()]
    tot_data_query = db.session.query(DeficitSurplus.total_outlay).order_by(DeficitSurplus.year)
    data_dict['total_outlays'] = [x[0] for x in tot_data_query.all()]
    tot_data_query = db.session.query(DeficitSurplus.total_net).order_by(DeficitSurplus.year)
    data_dict['total_net'] = [x[0] for x in tot_data_query.all()]
    return data_dict

def load_mysql_deficit_surplus():
    dataxls = pd.read_excel(os.path.join(EXCEL_DIR, BUDGET_1), index_col=None)
    for row_num, row in dataxls.iterrows():
        if row_num > BUDGET_ROW_THRESH:
            d = DeficitSurplus()
            try:
                d.year = int(row[0])
            except ValueError:
                print("Problem with Year")
                print(row)
                print()
                continue
            d.total_receipt = int(row[1])
            d.total_outlay = int(row[2])
            d.total_net = int(row[3])
            d.onbud_receipt = int(row[4])
            d.onbud_outlay = int(row[5])
            d.onbud_net = int(row[6])
            try:
                d.offbud_receipt = int(row[7])
                d.offbud_outlay = int(row[8])
                d.offbud_net = int(row[9])
            except ValueError:
                pass
            db.session.add(d)
            db.session.commit()

