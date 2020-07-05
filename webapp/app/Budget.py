import os
import pandas as pd
import numpy as np

# globals
CWD = os.path.dirname(os.path.abspath('__file__'))
EXCEL_DIR = os.path.join(CWD, '..', 'data', 'hist_fy21')
BUDGET_1 = 'hist01z1.xlsx'
EXCEL_FILES = sorted(os.listdir(EXCEL_DIR))
BUDGET_ROW_THRESH = 6


def read_data():
    dataxls = pd.read_excel(os.path.join(EXCEL_DIR, BUDGET_1), index_col=None)
    column_keys = ['year', 'Receipts', 'Outlays', 'Surplus or Deficit', 'Receipts', 'Outlays', 'Surplus or Deficit', 'Receipts', 'Outlays', 'Surplus or Deficit']

    data_dict = {}
    data_dict['Years'] = []
    data_dict['Total'] = {'Receipts': [], 'Outlays': [], 'Surplus or Deficit': []}
    data_dict['On-Budget'] = {'Receipts': [], 'Outlays': [], 'Surplus or Deficit': []}
    # data_dict['Off-Budget'] = {'Years': [], 'Receipts': [], 'Outlays': [], 'Surplus or Deficit': []}
    for row_num, row in dataxls.iterrows():
        if row_num > BUDGET_ROW_THRESH:
            try:
                data_dict['Years'].append(int(row[0]))
            except ValueError:
                continue
            data_dict['Total']['Receipts'].append(int(row[1]))
            data_dict['Total']['Outlays'].append(int(row[2]))
            data_dict['Total']['Surplus or Deficit'].append(int(row[3]))
            data_dict['On-Budget']['Receipts'].append(int(row[4]))
            data_dict['On-Budget']['Outlays'].append(int(row[5]))
            data_dict['On-Budget']['Surplus or Deficit'].append(int(row[6]))
    return data_dict
