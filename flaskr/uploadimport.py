from flask_sqlalchemy import SQLAlchemy
from numpy import logical_or
import datetime
import pandas as pd
from markupsafe import Markup
from dotenv import load_dotenv
import os
from .myfunx import genbefaf, histurl, getcurrent
import requests

from pymysql import NULL
load_dotenv
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI_DEBUG')
f_api_key = os.environ.get('f_api_key')
# SQLALCHEMY_DATABASE_URI=str('mysql+pymysql://') + USERNAME + str(':') + PASSWORD + str('@') + HOST + str(':') + PORT + str('/') + DATABASE

app, db = createapp()

from collections import OrderedDict, defaultdict
import json
from itertools import groupby
import calendar

#declare some variables
routeedate = ''
now = datetime.datetime.now()
staticstrike = 10
lists = {}

def prepimport():
    thedfprepped = thedf
    thedfprepped.reset_index
    thedfprepped = thedfprepped.drop(columns=['Implied Move', 'Implied Move Relative to 4-Qtr Avg', 'Implied Move Relative to 12-Qtr Avg', 'Implied Move Relative to 12-Qtr Median', 'Abs. Avg Implied Move', 'Abs. Avg Actual Move', 'Abs. Max Actual Move', 'Abs. Min Actual Move', 'Abs. Avg Implied Move.1', 'Abs. Avg Actual Move.1', 'Abs. Median Actual Move', 'Abs. Max Actual Move.1', 'Abs. Min Actual Move.1', 'Current Price', 'InWatchlist', 'EtfHoldingsList', 'Sector', 'Industry', 'Diff_ImpliedVsLast4AvgImplied', 'Diff_ImpliedVsLast12AvgImplied'])
    thedfprepped[['beforedate', 'afterdate']] = '',''
    thedfprepped['Earnings Date'] = pd.to_datetime(thedfprepped['Earnings Date'])
    thedfprepped['bmoamc'] = thedfprepped['bmoamc'].replace('BMO', '8:00:00')
    thedfprepped['bmoamc'] = thedfprepped['bmoamc'].replace('AMC', '16:00:00')
    thedfprepped['Earnings Date'] = thedfprepped['Earnings Date'].astype(str) + ' ' + thedfprepped['bmoamc'].astype(str)
    thedfprepped[['expiry', 'strike', 'iv', 'straddlemid', 'impliedmove', 'underlyingprice']] = '','','','','',''
    for index, row in thedfprepped.iterrows():
        targetdate = row['Earnings Date']
        targetdate = datetime.datetime.strptime(targetdate, '%Y-%m-%d %H:%M:%S')
        theticker = row['Symbol']
        beforedate, afterdate = genbefaf(targetdate)
        thedfprepped.at[index, 'beforedate'] = beforedate
        thedfprepped.at[index, 'afterdate'] = afterdate
    for index, row in thedfprepped.iterrows():
        targetdate = row['Earnings Date']
        theticker = row['Symbol']
        expiry, strike, iv, straddlemid, impliedmove, underlyingprice = getcurrent(theticker, row['beforedate'])
        thedfprepped.at[index, 'expiry'] = expiry
        thedfprepped.at[index, 'strike'] = strike
        thedfprepped.at[index, 'iv'] = iv
        thedfprepped.at[index, 'straddlemid'] = straddlemid
        thedfprepped.at[index, 'impliedmove'] = impliedmove
        thedfprepped.at[index, 'underlyingprice'] = underlyingprice
    thedfprepped['Earnings Date'] = thedfprepped['Earnings Date']