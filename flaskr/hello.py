from site import setcopyright
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from matplotlib import image
from numpy import logical_or
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
    company_name = db.Column(db.String(255))
    avg_optvol = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    avg_stockvol = db.Column(db.Float)
    sector = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    address = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    zipcode = db.Column(db.String(10))
    description = db.Column(db.Text(255))
    updated = db.Column(db.String())
    isactivelytrading = db.Column(db.Integer())
    logo = db.Column(db.String(255))
    website = db.Column(db.String(255))

class earningsdates(db.Model):
    earningsdateid = db.Column(db.Integer(), primary_key=True)
    ticker = db.Column(db.String(15))
    companyname = db.Column(db.String(100))
    exactearningsdate = db.Column(db.String())

@app.route('/<string:ticker>')
def hello(ticker):
    try:
        mresult = Main.query.filter(Main.ticker==ticker).first()
        company_name = mresult.company_name
        avg_optvol = mresult.avg_optvol
        market_cap = round((mresult.market_cap/1000000000), 2)
        avg_stockvol = mresult.avg_stockvol
        theticker = mresult.ticker
        sector = mresult.sector
        industry = mresult.industry
        address = mresult.address
        city = mresult.city
        state = mresult.state
        zipcode = mresult.zipcode
        description = mresult.description
        logo = mresult.logo
        website = mresult.website
    except:
        pass
    edate = earningsdates.query.filter_by(ticker = ticker).order_by(earningsdates.exactearningsdate.desc()).first()

    exactearningsdate = edate.exactearningsdate
    edatestr = datetime.datetime.strftime(exactearningsdate,'%-m/%-d/%Y %-H')
    thisticker = edate.ticker
    edatestr, bmoamc = edatestr.split()
    bmoamc = bmoamc.replace('8', 'Before Market Open')
    bmoamc = bmoamc.replace('16', 'After Market Close')
    now = datetime.datetime.now()

    #query
    eresult = earningsdates.query \
        .with_entities(earningsdates.ticker, earningsdates.exactearningsdate, earningsdates.companyname) \
        .filter(earningsdates.exactearningsdate > now).order_by(earningsdates.ticker).all()
    
    df = pd.DataFrame(eresult, columns =['ticker', 'exactearningsdate', 'companyname'])
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
            companyname = company_name,
            avg_optvol = f'{int(avg_optvol):,}',
            market_cap = market_cap,
            avg_stockvol = f'{int(avg_stockvol):,}',
            earningsdate = edatestr,
            bmoamc = bmoamc,
            sector = sector,
            industry = industry,
            address = address,
            city = city,
            state = state,
            zipcode = zipcode,
            description = description,
            logo = logo,
            website = website,
            lists = lists)
    except:
        return render_template('index.html', 
            companyname = "This doesn't exist",
            lists=lists)        
