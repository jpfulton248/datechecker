from random import randint
from site import setcopyright
from ssl import ALERT_DESCRIPTION_ACCESS_DENIED, CHANNEL_BINDING_TYPES
from token import EXACT_TOKEN_TYPES
from flask import Flask, current_app, render_template, url_for, redirect, request, Response
from flask_sqlalchemy import SQLAlchemy
from matplotlib import image
from numpy import logical_or
import datetime
import pandas as pd
from markupsafe import Markup
import re
from dotenv import load_dotenv
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from sqlalchemy import false, true
import requests
import io

from pymysql import NULL
load_dotenv
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
#local
# SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI_DEBUG')
f_api_key = os.environ.get('f_api_key')
# SQLALCHEMY_DATABASE_URI=str('mysql+pymysql://') + USERNAME + str(':') + PASSWORD + str('@') + HOST + str(':') + PORT + str('/') + DATABASE
app=Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI
db=SQLAlchemy(app)
from collections import OrderedDict, defaultdict
import json
from itertools import groupby
import calendar

#declare some variables
routeedate = ''
now = datetime.datetime.now()
staticstrike = 10
lists = {}

class alldates(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    ticker = db.Column(db.String(255))
    edate = db.Column(db.String(255))
    bmoamc = db.Column(db.String(255))

# @app.route('/', methods=['GET', 'POST'])
# def check():
#     if request.method == 'POST':
#         file = request.files['file']        
#         kdf = pd.read_csv(file, header=0, names=['kticker', 'kedate', 'kbmoamc'])
#         kdf.fillna('None', inplace=True)
#         mydict = {"ticker":[],"correct_date":[],"correct_time":[],"kedate":[],"kbmoamc":[], "issue": []}
#         for index, row in kdf.iterrows():
#             kticker = row['kticker']
#             kedate = row['kedate']
#             kbmoamc = row['kbmoamc']
#             ticker = ''
#             edate = ''
#             bmoamc = ''
#             q = alldates.query.with_entities(alldates.ticker, alldates.edate, alldates.bmoamc).filter(alldates.ticker == kticker).all()
#             if q:
#                 ticker = q[0][0]
#                 edate = q[0][1]
#                 bmoamc = q[0][2]
#             if kedate == edate and bmoamc == kbmoamc and bmoamc != 'None':
#                 mydict["ticker"].append(kticker)
#                 mydict["correct_date"].append(edate)
#                 mydict["correct_time"].append(bmoamc)
#                 mydict["kedate"].append(kedate)
#                 mydict["kbmoamc"].append(kbmoamc)
#                 mydict["issue"].append(str('No Issues'))
#             elif kedate == edate and bmoamc == None:
#                 mydict["ticker"].append(kticker)
#                 mydict["correct_date"].append(edate)
#                 mydict["correct_time"].append(bmoamc)
#                 mydict["kedate"].append(kedate)
#                 mydict["kbmoamc"].append(kbmoamc)
#                 mydict["issue"].append(str('Date is Correct. Time unknown.'))
#             elif kedate != edate and bmoamc == kbmoamc:
#                 mydict["ticker"].append(kticker)
#                 mydict["correct_date"].append(edate)
#                 mydict["correct_time"].append(bmoamc)
#                 mydict["kedate"].append(kedate)
#                 mydict["kbmoamc"].append(kbmoamc)
#                 mydict["issue"].append(str('Date is Incorrect. Time is Correct'))
#             elif kedate == edate and bmoamc != kbmoamc:
#                 mydict["ticker"].append(kticker)
#                 mydict["correct_date"].append(edate)
#                 mydict["correct_time"].append(bmoamc)
#                 mydict["kedate"].append(kedate)
#                 mydict["kbmoamc"].append(kbmoamc)
#                 mydict["issue"].append(str('Date is Correct. Time is Incorrect'))
#             elif kedate != edate and bmoamc != kbmoamc:
#                 mydict["ticker"].append(kticker)
#                 mydict["correct_date"].append(edate)
#                 mydict["correct_time"].append(bmoamc)
#                 mydict["kedate"].append(kedate)
#                 mydict["kbmoamc"].append(kbmoamc)
#                 mydict["issue"].append(str('Date and time are both incorrect'))
#             else:
#                 mydict["ticker"].append(kticker)
#                 mydict["correct_date"].append(edate)
#                 mydict["correct_time"].append(bmoamc)
#                 mydict["kedate"].append(kedate)
#                 mydict["kbmoamc"].append(kbmoamc)
#                 mydict["issue"].append(str('Issue unclear'))
#         resultsdf = pd.DataFrame.from_dict(mydict)
#         return render_template('index.html', outputted=resultsdf.to_html(classes='display table table-dark sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'))
#     return render_template('index.html')

# @app.route('/import', methods=['GET', 'POST'])
# def imp():
#     if request.method == 'POST':
#         file = request.files['file']        
#         df = pd.read_csv(file, header=0, names=['ticker', 'Name', 'MarketCap', 'SP500', 'QtrNext', 'IsProjectedNext', 'IsAnnouncedNext', 'edate', 'bmoamc', 'ConfCallNext', 'ExpectedMoveNext', 'ActualMovePrev', 'ExpectedMovePrev', 'QtrPrev', 'DatePrev', 'TimePrev', 'ConfCallPrev', 'SECFiling', 'StockType', 'HasOptions'])
#         df = df[['ticker', 'edate', 'bmoamc']]
#         df['edate']=pd.to_datetime(df['edate'].astype(str), format='%m/%d/%Y')
#         # Conver DataTime to Different Format
#         df['edate'] = df['edate'].dt.strftime('%Y-%m-%d')
#         df.to_sql('alldates', con=db.engine, if_exists='replace', index=True)
#         return render_template('import.html', imported=df.to_html(classes='display table table-dark sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'))
#     return render_template('import.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        mydict = {"ticker":[],"correct_date":[],"correct_time":[],"kedate":[],"kbmoamc":[], "issue": []}
        incoming = request.form['text']
        incoming = io.StringIO(incoming)
        incoming = incoming.read()
        try:
            incoming = str(incoming).splitlines()
        except:
            pass
        for row in incoming:
            edate = ''
            bmoamc = ''
            kticker = ''
            kedate = ''
            kbmoamc = ''
            kticker, kedate, kbmoamc = row.split(",")
            try:
                kticker = str.upper(kticker)
                kbmoamc = str.upper(kbmoamc)
            except:
                pass
            q = alldates.query.with_entities(alldates.ticker, alldates.edate, alldates.bmoamc).filter(alldates.ticker == kticker).all()
            if q:
                edate = q[0][1]
                bmoamc = q[0][2]
                if bmoamc:
                    bmoamc = str.upper(bmoamc)
            if kedate == edate and bmoamc == kbmoamc and bmoamc != 'None':
                mydict["ticker"].append(kticker)
                mydict["correct_date"].append(edate)
                mydict["correct_time"].append(bmoamc)
                mydict["kedate"].append(kedate)
                mydict["kbmoamc"].append(kbmoamc)
                mydict["issue"].append(str('No Issues'))
            elif kedate == edate and bmoamc == None:
                mydict["ticker"].append(kticker)
                mydict["correct_date"].append(edate)
                mydict["correct_time"].append(bmoamc)
                mydict["kedate"].append(kedate)
                mydict["kbmoamc"].append(kbmoamc)
                mydict["issue"].append(str('Date is Correct. Time unknown.'))
            elif kedate != edate and bmoamc == kbmoamc:
                mydict["ticker"].append(kticker)
                mydict["correct_date"].append(edate)
                mydict["correct_time"].append(bmoamc)
                mydict["kedate"].append(kedate)
                mydict["kbmoamc"].append(kbmoamc)
                mydict["issue"].append(str('Date is Incorrect. Time is Correct'))
            elif kedate == edate and bmoamc != kbmoamc:
                mydict["ticker"].append(kticker)
                mydict["correct_date"].append(edate)
                mydict["correct_time"].append(bmoamc)
                mydict["kedate"].append(kedate)
                mydict["kbmoamc"].append(kbmoamc)
                mydict["issue"].append(str('Date is Correct. Time is Incorrect'))
            elif kedate != edate and bmoamc != kbmoamc and edate != '':
                mydict["ticker"].append(kticker)
                mydict["correct_date"].append(edate)
                mydict["correct_time"].append(bmoamc)
                mydict["kedate"].append(kedate)
                mydict["kbmoamc"].append(kbmoamc)
                mydict["issue"].append(str('Date and time are both incorrect'))
            elif kedate != edate and bmoamc != kbmoamc and edate == '':
                mydict["ticker"].append(kticker)
                mydict["correct_date"].append(edate)
                mydict["correct_time"].append(bmoamc)
                mydict["kedate"].append(kedate)
                mydict["kbmoamc"].append(kbmoamc)
                mydict["issue"].append(str('Correct date not found. Earnings date likely not announced.'))
            else:
                mydict["ticker"].append(kticker)
                mydict["correct_date"].append(edate)
                mydict["correct_time"].append(bmoamc)
                mydict["kedate"].append(kedate)
                mydict["kbmoamc"].append(kbmoamc)
                mydict["issue"].append(str('Issue unclear'))
        resultsdf = pd.DataFrame.from_dict(mydict)
        filtereddf = resultsdf.copy(deep=True)
        filtereddf = filtereddf[filtereddf.issue != 'No Issues']
        good = str('good')
        return render_template('index.html', good=good, outputted=resultsdf.to_html(classes='display table table-light sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'), filteredtable=filtereddf.to_html(classes='display table table-light sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'))
    return render_template('index.html')

@app.route('/import', methods=['GET', 'POST'])
def imp():
    if request.method == 'POST':
        file = request.files['file']        
        df = pd.read_csv(file, header=0, names=['ticker', 'Name', 'MarketCap', 'SP500', 'QtrNext', 'IsProjectedNext', 'IsAnnouncedNext', 'edate', 'bmoamc', 'ConfCallNext', 'ExpectedMoveNext', 'ActualMovePrev', 'ExpectedMovePrev', 'QtrPrev', 'DatePrev', 'TimePrev', 'ConfCallPrev', 'SECFiling', 'StockType', 'HasOptions'])
        df = df[['ticker', 'edate', 'bmoamc']]
        df['edate']=pd.to_datetime(df['edate'].astype(str), format='%m/%d/%Y')
        # Conver DateTime to Different Format
        df['edate'] = df['edate'].dt.strftime('%Y-%m-%d')
        print(df)
        df.to_sql('alldates', con=db.engine, if_exists='replace', index=True)
        return render_template('import.html', imported=df.to_html(classes='display table table-dark sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'))
    return render_template('import.html')