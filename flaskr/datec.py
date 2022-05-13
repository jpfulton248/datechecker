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
import markdown
from functools import wraps
import asyncio
import pyperclip as pc
import asyncio
from pymysql import NULL
from aiohttp import ClientSession
import aiohttp
import ssl
import certifi

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

urls = ['http://127.0.0.1/test']

# Helper Functions

client = aiohttp.ClientSession()


import aiohttp
import asyncio
import ssl
import certifi



# @app.route('/test2')
# async def main(url):
#     ssl_context = ssl.create_default_context(cafile=certifi.where())
#     conn = aiohttp.TCPConnector(ssl=ssl_context)
#     async with aiohttp.ClientSession(connector=conn) as session:
#         async with session.get(url) as response:
#             print("Status:", response.status)

# url = "https://shikimori.one/"
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main(url))

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
    projected = db.Column(db.String(255))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        mydict = {"ticker":[],"correct_date":[],"correct_time":[],"kedate":[],"kbmoamc":[], "issue": [], "forfilter": []}
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
            issues = ''
            forfilter = ''
            kticker, kedate, kbmoamc = row.split(",")
            try:
                kticker = str.upper(kticker)
                kbmoamc = str.upper(kbmoamc)
            except:
                pass
            q = alldates.query.with_entities(alldates.ticker, alldates.edate, alldates.bmoamc, alldates.projected).filter(alldates.ticker == kticker).all()
            if q:
                edate = q[0][1]
                bmoamc = q[0][2]
                projected = q[0][3]
                if bmoamc:
                    bmoamc = str.upper(bmoamc)
            if kedate == edate and bmoamc == kbmoamc and bmoamc != 'None':
                issues = str('No Issues')
                forfilter = str('Include')
            if kedate == edate and bmoamc == 'None':
                issues = str('Date is Correct. Time unknown.')
                forfilter = str('Include')
            if kedate != edate and bmoamc == kbmoamc and edate != 'None':
                issues = str('Date is Incorrect. Time is Correct')
                forfilter = str('Include')
            if kedate == edate and bmoamc != kbmoamc and bmoamc != 'None':
                issues = str('Date is Correct. Time is Incorrect')
            if kedate != edate and bmoamc != kbmoamc and edate != '':
                issues = str('Date and time are both incorrect')
                forfilter = str('Include')
            if edate == '':
                print('bad one')
                issues = str('Date not found. Earnings date likely not announced.')
                forfilter = str('Exclude')
            if projected == 1:
                issues = str('Projected. Not Confirmed.')
                forfilter = str('Exclude')
            # else:
            #     issues = str('Issue unclear')
            #     forfilter = str('Exclude')
            mydict["ticker"].append(kticker)
            mydict["correct_date"].append(edate)
            mydict["correct_time"].append(bmoamc)
            mydict["kedate"].append(kedate)
            mydict["kbmoamc"].append(kbmoamc)
            mydict["issue"].append(issues)
            mydict["forfilter"].append(forfilter)
        completedf = pd.DataFrame.from_dict(mydict)
        issuesdf = completedf.copy(deep=True)
        issuesdf = issuesdf[issuesdf.issue != 'No Issues']
        noissuesdf = completedf.copy(deep=True)
        noissuesdf = noissuesdf[noissuesdf.forfilter == 'Include']
        noissuesdf.drop(columns=['forfilter'], inplace=True)
        completedf.drop(columns=['forfilter'], inplace=True)
        issuesdf.drop(columns=['forfilter'], inplace=True)
        good = str('good')
        completecnt = len(completedf.index)
        issuescnt = len(issuesdf.index)
        noissuescnt = len(noissuesdf.index)
        goodresultsdf = noissuesdf[['ticker','correct_date','correct_time']]
        goodresultsdf.to_csv('flaskr/static/goodresults.txt', index=False, header=None)
        return render_template('index.html', good=good, completecnt=completecnt, noissuescnt=noissuescnt, issuescnt=issuescnt, complete=completedf.to_html(classes='display table table-light sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'), issues=issuesdf.to_html(classes='display table table-light sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'), noissues=noissuesdf.to_html(classes='display table table-light sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'))
    return render_template('index.html')

@app.route('/import', methods=['GET', 'POST'])
def imp():
    if request.method == 'POST':
        file = request.files['file']        
        df = pd.read_csv(file, header=0, names=['ticker', 'Name', 'MarketCap', 'SP500', 'QtrNext', 'projected', 'IsAnnouncedNext', 'edate', 'bmoamc', 'ConfCallNext', 'ExpectedMoveNext', 'ActualMovePrev', 'ExpectedMovePrev', 'QtrPrev', 'DatePrev', 'TimePrev', 'ConfCallPrev', 'SECFiling', 'StockType', 'hasoptions'])
        df = df[['ticker', 'edate', 'bmoamc', 'projected']]
        df['edate']=pd.to_datetime(df['edate'].astype(str), format='%m/%d/%Y')
        # Convert DateTime to Different Format
        df['edate'] = df['edate'].dt.strftime('%Y-%m-%d')
        print(df)
        df.to_sql('alldates', con=db.engine, if_exists='replace', index=True)
        return render_template('import.html', imported=df.to_html(classes='display table table-dark sortable table-striped', table_id='sortit', escape=False, index=False, col_space=0, header=True, render_links=True, justify='center'))
    return render_template('import.html')

@app.route('/copy', methods=['GET', 'POST'])
def clipcopy():
    with open('flaskr/static/goodresults.txt') as f:
        data=''.join(line.rstrip() for line in f)
    pc.copy(data)






# def multiline(fn):
#     @wraps(fn)
#     def _fn(*args, **kwargs):
#         return "<pre>" + fn(*args, **kwargs) + "</pre>"
#     return _fn

# @app.route('/test')
# @multiline
# def testit():
#     one = str('one')
#     two = str('two')
#     three = str('three')
#     four = str('four')
#     five = str('five')
#     six = str('six')
#     seven = str('seven')
#     eight = str('eight')
#     nine = str('nine')
#     ten = str('ten')
#     eleven = str('elevn')
#     twelve = str('twelve')
#     thirteen = str('thirteen')
#     fourteen = str('fourteen')
#     fifteen = str('fifteen')
#     sixteen = str('sixteen')
#     seventeen = str('seventeen')
#     out = """[{} moves an average of **+/-{}%** around earnings] (https://earnings-watcher.com/#/moves?symbol={}), with a

#     => *most past moves are between {}% and {}%, in absolute value*
#     &#x200B;

#     After earnings, stock price:

#     \- **kept same direction of move for {} days on average**

#     \- **reversed initial direction {}% of the time**

#     &#x200B;

#     Here are the last three earnings (absolute) moves and their durations:
#     \- *{}: {}% lasted for {} days*

#     \- *{}: {}% lasted for {} days*

#     vy \- *{}: {}% lasted for {} days*""".format(one,
#                                                 two,
#                                                 three,
#                                                 four,
#                                                 five,
#                                                 six,
#                                                 seven,
#                                                 eight,
#                                                 nine,
#                                                 ten,
#                                                 eleven,
#                                                 twelve,
#                                                 thirteen,
#                                                 fourteen,
#                                                 fifteen,
#                                                 sixteen,
#                                                 seventeen)
#     return str(out)

# @test2