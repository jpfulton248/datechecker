from site import setcopyright
from flask import Flask, current_app, render_template, url_for, redirect, request
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

#declare some variables
routeedate = ''
now = datetime.datetime.now()
staticstrike = 10
lists = {}


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

class changes(db.Model):
    changesid = db.Column(db.Integer(), primary_key=True)
    ticker = db.Column(db.String())
    dated = db.Column(db.String())
    iv = db.Column(db.Numeric(10,2))
    straddle = db.Column(db.Numeric(10,2))
    impliedmove = db.Column(db.Numeric(10,2))
    underlying = db.Column(db.Numeric(10,2))
    strike = db.Column(db.Numeric(10,2))
    quarter = db.Column(db.String())

class ridingstraddle(db.Model):
    rdid = db.Column(db.Integer(), primary_key=True)
    ticker = db.Column(db.String())
    exactearningsdate = db.Column(db.String())
    staticstraddle = db.Column(db.Numeric(10,2))
    staticiv = db.Column(db.Numeric(10,2))
    underlying = db.Column(db.Numeric(10,2))
    staticstrike = db.Column(db.Numeric(10,2))
    dated = db.Column(db.String())


@app.route('/<string:ticker>')
def hello(ticker):
    routeticker = ticker
    try:
        mresult = Main.query.filter(Main.ticker==routeticker).first()
        company_name = mresult.company_name
        avg_optvol = mresult.avg_optvol
        market_cap = round((mresult.market_cap/1000000000), 2)
        avg_stockvol = mresult.avg_stockvol
    #   theticker = mresult.ticker
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

    #####MAINCONTENT#####
    #This is for loading all the stats in main content
    with app.test_request_context('/'), app.test_client() as c:
        routeticker = request.path
    routeticker = routeticker
    routeticker = 'ADBE'
    edate = earningsdates.query. \
        with_entities(earningsdates.ticker, earningsdates.companyname, earningsdates.exactearningsdate). \
            filter(earningsdates.ticker == routeticker).order_by(earningsdates.exactearningsdate. \
            desc()).first()
    mcdf = pd.DataFrame(edate, columns=['ticker', 'companyname', 'exactearningsdate'])
    mcdf.iterrows:
        
    edatestr = datetime.datetime.strftime(exactearningsdate,'%-m/%-d/%Y %-H')
    edatestr, bmoamc = edatestr.split()
    bmoamc = bmoamc.replace('8', 'Before Market Open')
    bmoamc = bmoamc.replace('16', 'After Market Close')

    #####GETTING VALUES FROM FUNCTION RETURNS#####
    #sidebar
    sidemenu = sidebar()

    #static table and assign variable to get static strike
    stable = statictable()
    try:
        staticstrike = stable['Strike'].iloc[0]
    except:
        staticstrike = 10

    #changestable
    ctable = changestable()
    # cdf.to_html(classes='table table-light', escape=False, index=False, header=True, render_links=True)

    #####THE FINAL RENDERING OF /<ticker> TO INDEX.HTML#####
    return render_template('index.html', 
        routeticker = routeticker,
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
        tables = ctable,
        stables = stable.to_html(classes='table table-light', escape=False, index=False, header=True, render_links=True),
        lists = sidemenu,
        staticstrike = staticstrike)
    # except:
    #     return render_template('index.html', 
    #         companyname = "This doesn't exist",
    #         lists=lists)        

#####CHANGESTABLE#####
#CHANGES query this is all for loading the table of changes
def changestable():
    with app.test_request_context('/'), app.test_client() as c:
        routeticker = request.path
    cresult = changes.query \
        .with_entities(changes.dated, changes.iv, changes.straddle, changes.impliedmove, changes.underlying, changes.strike) \
        .filter(changes.ticker == routeticker).all()
    cdf = pd.DataFrame(cresult, columns =['Time', 'IV', 'Straddle Price', 'Implied Move', 'Stock Price', 'Strike'])
    cdf = cdf.sort_values(['Time'], ascending=[False])
    cdf['Time'] = cdf['Time'].apply(lambda x: x.strftime('%-m/%-d/%-y %-I:%M %p'))
    cdf = cdf.to_html(classes='table table-light', escape=False, index=False, header=True, render_links=True)
    print(routeticker)
    return cdf
changestable()

#####STATIC TABLE#####
#STATIC TABLE query this is all for loading the table of changes
def statictable():
    #####STATICTABLE#####
    #STATIC query this is all for loading the table of changes
    sresult = ridingstraddle.query \
        .with_entities(ridingstraddle.dated, ridingstraddle.staticiv, ridingstraddle.staticstraddle, ridingstraddle.underlying, ridingstraddle.staticstrike) \
        .filter(ridingstraddle.ticker == routeticker).all()
    sdf = pd.DataFrame(sresult, columns =['Time', 'IV', 'Straddle Price', 'Stock Price', 'Strike'])
    sdf = sdf.sort_values(['Time'], ascending=[False])
    sdf['Time'] = sdf['Time'].apply(lambda x: x.strftime('%-m/%-d/%-y %-I:%M %p'))
    sdf.drop(columns='Strike')
    return sdf


#####SIDEBAR#####
#this is for loading the sidebar
def sidebar():
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
    for k, g in groupby(mydict, key=lambda t: t['earningsdow']):
        lists[k] = list(g)
    return lists