from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from config import sqlalchemyurl
import datetime
import pandas as pd
from markupsafe import Markup
import re
app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemyurl
db = SQLAlchemy(app)
from collections import OrderedDict, defaultdict
import json
from itertools import groupby
import calendar

class Main(db.Model):
    mainid = db.Column(db.Integer(), primary_key=True)
    ticker = db.Column(db.String(15))
    company_name = db.Column(db.String(50))
    avg_optvol = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    avg_stockvol = db.Column(db.Float)

class earningsdates(db.Model):
    earningsdateid = db.Column(db.Integer(), primary_key=True)
    ticker = db.Column(db.String(15))
    companyname = db.Column(db.String(100))
    exactearningsdate = db.Column(db.String())

@app.route('/<string:ticker>')
def hello(ticker):
    try:
        theticker =  Main.query.filter_by(ticker = ticker).first()
        companyname = theticker.company_name
        avg_optvol = theticker.avg_optvol
        market_cap = theticker.market_cap
        avg_stockvol = theticker.avg_stockvol
        theticker = theticker.ticker
        market_cap = round((market_cap/1000000000), 2)
    except:
        pass
    edate = earningsdates.query.filter_by(ticker = ticker).first()
    exactearningsdate = edate.exactearningsdate
    edatestr = datetime.datetime.strftime(exactearningsdate,'%-m/%-d/%Y %-H')
    thisticker = edate.ticker
    edatestr, bmoamc = edatestr.split()
    bmoamc = bmoamc.replace('8', 'Before Market Open')
    bmoamc = bmoamc.replace('16', 'After Market Close')
    now = datetime.datetime.now()
    result = earningsdates.query \
        .with_entities(earningsdates.ticker, earningsdates.exactearningsdate, earningsdates.companyname) \
        .filter(earningsdates.exactearningsdate > now).order_by(earningsdates.ticker).all()
    
    df = pd.DataFrame(result, columns =['ticker', 'exactearningsdate', 'companyname'])
    df['exactearningsdatestr'] = df['exactearningsdate'].dt.strftime('%-m/%-d/%-y %-H')
    df['earningsdow'] = df['exactearningsdate'].dt.day_name()
    df[['exactearningsdatestr', 'time']] = df['exactearningsdatestr'].str.split(' ', n=1, expand=True)
    df['time'] = df['time'].replace('8', 'BMO')
    df['time'] = df['time'].replace('16', 'AMC')
    df = df.sort_values(['exactearningsdatestr', 'time'], ascending=[True, False])
    df = df.drop(columns='exactearningsdate')
    mydict = df.to_dict(orient='rows')

    lists = {}

    for k, g in groupby(mydict, key=lambda t: t['earningsdow']):
        lists[k] = list(g)

    try:
        return render_template('index.html', 
            theticker = thisticker,
            companyname = companyname,
            avg_optvol = f'{int(avg_optvol):,}',
            market_cap = market_cap,
            avg_stockvol = f'{int(avg_stockvol):,}',
            earningsdate = edatestr,
            bmoamc = bmoamc,
            lists = lists)
    except:
        return render_template('index.html', 
            companyname = "This doesn't exist",
            lists=lists)        