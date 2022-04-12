from site import setcopyright
from ssl import ALERT_DESCRIPTION_ACCESS_DENIED
from flask import Flask, current_app, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from matplotlib import image
from numpy import logical_or
# from config import sqlalchemyurl
import datetime
import pandas as pd
from markupsafe import Markup
import re
from dotenv import load_dotenv
import os

from pymysql import NULL
load_dotenv
# USERNAME = os.environ.get('USERNAME')
# HOST = os.environ.get('HOST')
# DATABASE = os.environ.get('DATABASE')
# PASSWORD = os.environ.get('PASSWORD')
# PORT = os.environ.get('PORT')
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
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
    beforedate = db.Column(db.String())
    closebefore = db.Column(db.String())
    afterdate = db.Column(db.String())
    openafter = db.Column(db.Numeric(20,2))
    highafter = db.Column(db.Numeric(20,2))
    lowafter = db.Column(db.Numeric(20,2))
    closeafter = db.Column(db.String())
    actualmove = db.Column(db.Numeric(20,2))
    actualmoveperc = db.Column(db.Numeric(20,2))
    averageoptionvol = db.Column(db.Float())
    averagestockvol = db.Column(db.Float())
    marketcap = db.Column(db.Numeric(20,2))
    impliedmove = db.Column(db.Numeric(20,2))
    staticstrike = db.Column(db.Numeric(20,2))
    staticexpiry = db.Column(db.String())
    staticprice = db.Column(db.Numeric(20,2))
    staticunderlying = db.Column(db.Numeric(10,2))
    staticiv = db.Column(db.Numeric(20,2))
    updated = db.Column(db.String())

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

def now():
    now = datetime.datetime.now()
    return now

def yesterday():
    yesterday = now() - datetime.timedelta(days=1)
    return yesterday

def sidebar():
    try:
        eresult = earningsdates.query \
            .with_entities(earningsdates.ticker, earningsdates.exactearningsdate, earningsdates.companyname) \
            .filter(earningsdates.exactearningsdate > yesterday()).order_by(earningsdates.ticker).all()
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
        return lists
    except:
        noearnings = str('no earnings yet')
        return noearnings

def maincontent(routeticker):
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
        website = '<a href="' + str(website) + '">' + str(website) + '</a>'
    except:
        pass
    edate = earningsdates.query.filter(earningsdates.ticker==routeticker).order_by(earningsdates.exactearningsdate.desc()).first()
    exactearningsdate = edate.exactearningsdate
    edatestr = datetime.datetime.strftime(exactearningsdate,'%-m/%-d/%Y %-H')
    edatestr, bmoamc = edatestr.split()
    bmoamc = bmoamc.replace('8', 'Before Market Open')
    bmoamc = bmoamc.replace('16', 'After Market Close')
    maincontentvars = [company_name, avg_optvol, market_cap, avg_stockvol, sector, industry, address, city, state, zipcode, description, logo, website, edatestr, bmoamc]
    return maincontentvars

def changestable(routeticker):
    try:
        cresult = changes.query \
            .with_entities(changes.dated, changes.iv, changes.straddle, changes.impliedmove, changes.underlying, changes.strike) \
            .filter(changes.ticker == routeticker).all()
        changestable = pd.DataFrame(cresult, columns=['Time', 'IV', 'Straddle Price', 'Implied Move', 'Stock Price', 'Strike'])
        changestable = changestable.sort_values(['Time'], ascending=[False])
        changestable = changestable.reset_index(drop=True)
        changestable['Time'] = changestable['Time'].dt.strftime("%-m/%-d/%-y %-I:%M %p")
        ctable = changestable
    except:
        ctable = pd.DataFrame()
    return ctable

def statictable(routeticker):
    try:
        sresult = ridingstraddle.query \
            .with_entities(ridingstraddle.dated, ridingstraddle.staticiv, ridingstraddle.staticstraddle, ridingstraddle.underlying, ridingstraddle.staticstrike) \
            .filter(ridingstraddle.ticker == routeticker).all()
        sdf = pd.DataFrame(sresult, columns =['Time', 'IV', 'Straddle Price', 'Stock Price', 'Strike'])
        sdf = sdf.sort_values(['Time'], ascending=[False])
        sdf['Time'] = sdf['Time'].apply(lambda x: x.strftime('%-m/%-d/%-y %-I:%M %p'))
        sdf.drop(columns='Strike')
    except:
        sdf = pd.DataFrame()
    return sdf

def historical(routeticker):
    eresult = earningsdates.query \
            .with_entities(earningsdates.ticker, earningsdates.exactearningsdate, earningsdates.actualmoveperc) \
            .filter(earningsdates.ticker == routeticker, earningsdates.closeafter != NULL).all()
    df = pd.DataFrame(eresult, columns=['Ticker', 'EarningsDate', 'ActualMovePerc'])
    df = df.sort_values(['EarningsDate'], ascending=[False])
    #line below can be used to limit history
    df = df.head(40)
    df = df.sort_values(['EarningsDate'], ascending=[True])
    df.reset_index(drop=True, inplace=True)
    df['CumulativeActMovePerc'] = df.groupby('Ticker')['ActualMovePerc'].expanding().mean().values
    # df['StdDev'] = df.groupby('Ticker')['ActualMovePerc'].expanding().std().values
    df['CumulativeActMovePerc'] = df['CumulativeActMovePerc'].astype(float).abs()
    df = df.sort_values(['EarningsDate'], ascending=[False])
    df.reset_index(drop=True, inplace=True)
    cumabsavgperc = df.at[0, 'CumulativeActMovePerc']
    countreports = len(df.index)
    return cumabsavgperc, countreports

@app.route("/search", methods=["POST", "GET"])
def home():
    if request.method == "GET":
        thechoices = Main.query.with_entities(Main.ticker).all()
        thechoices = pd.DataFrame(thechoices, columns=['choice'], index=None)
        choiceoption = thechoices['choice'].tolist()
    return render_template("search.html", languages=choiceoption)

@app.route("/search", methods=["GET", "POST"])
def home2():
    if request.method == "POST":
        text = request.form['text']
        processed_text = text.upper()
        print(processed_text)
        return processed_text

    #changestable
    ctable = changestable()
    # cdf.to_html(classes='table table-light', escape=False, index=False, header=True, render_links=True)

@app.route('/<string:routeticker>', methods=['POST', 'GET'])
def mainroute(routeticker):
    sidebarlist = sidebar()
    company_name, avg_optvol, market_cap, avg_stockvol, sector, industry, address, city, state, zipcode, description, logo, website, edatestr, bmoamc = maincontent(routeticker)
    ctable = changestable(routeticker)
    try:
        impmove = ctable.at[0, 'Implied Move']
    except:
        impmove = ''
    cumabsavgperc, countreports = historical(routeticker)
    if impmove != '':
        underover =  float(cumabsavgperc) - float(impmove)
    else:
        underover = ''
    # historicalresult = historical(routeticker)

    # stable = statictable(routeticker)
    
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
        absactualmoveperc = round(cumabsavgperc,2),
        countreports = countreports,
        underover = round(underover,2),
        impmove = impmove,
        # historicalresult = historicalresult.to_html(classes='table table-light', escape=False, index=False, header=True, render_links=True),
        ctable = ctable.to_html(classes='table table-light', escape=False, index=True, header=True, render_links=True),
        # stable = stable.to_html(classes='table table-light', escape=False, index=False, header=True, render_links=True),
        lists = sidebarlist)

@app.route('/')
def screener():
    l = earningsdates.query \
            .with_entities(earningsdates.ticker, earningsdates.exactearningsdate, earningsdates.companyname, earningsdates.averageoptionvol, \
                earningsdates.averagestockvol, earningsdates.marketcap, earningsdates.impliedmove) \
            .filter(earningsdates.exactearningsdate > yesterday()).order_by(earningsdates.ticker).all()
    df = pd.DataFrame(l)
    if df.empty:
        print('DataFrame is empty!')
    else:
        df['companyname'] = df['companyname'].str[:40]
        df['ticker'] = '<a href="' + df['ticker'].astype(str) + '" style="color:#FFFFFF;">' + df['ticker'].astype(str) + '</a>'
        df['marketcap'] = df['marketcap'].div(1000000000)
        df['date'] = df['exactearningsdate'].dt.strftime('%-m/%-d/%-y %-H')
        df[['date', 'time']] = df['date'].str.split(' ', n=1, expand=True)
        df['time'] = df['time'].replace('8', 'BMO')
        df['time'] = df['time'].replace('16', 'AMC')
        df = df.sort_values(['date', 'time'], ascending=[True, False])
        df = df.drop(columns=['exactearningsdate', 'impliedmove'])
        pd.options.display.float_format = '{:,}'.format 
        pd.options.display.float_format = '{:,.0f}'.format 
        return render_template('screener.html', screener=df.to_html(classes='table table-dark sortable table-striped display', table_id='sortit', escape=False, index=False, header=True, render_links=True, justify='left'), lists = sidebar())


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global thedf
    if request.method == 'POST':
        file = request.files['file']        
        thedf = pd.read_csv(file)
        thedf.reset_index
        thedf = thedf.drop(columns=['Implied Move', 'Implied Move Relative to 4-Qtr Avg', 'Implied Move Relative to 12-Qtr Avg', 'Implied Move Relative to 12-Qtr Median', 'Abs. Avg Implied Move', 'Abs. Avg Actual Move', 'Abs. Max Actual Move', 'Abs. Min Actual Move', 'Abs. Avg Implied Move.1', 'Abs. Avg Actual Move.1', 'Abs. Median Actual Move', 'Abs. Max Actual Move.1', 'Abs. Min Actual Move.1', 'Current Price', 'InWatchlist', 'EtfHoldingsList', 'Sector', 'Industry', 'Diff_ImpliedVsLast4AvgImplied', 'Diff_ImpliedVsLast12AvgImplied'])
        thedf['Earnings Date'] = pd.to_datetime(thedf['Earnings Date'])
        thedf['bmoamc'] = thedf['bmoamc'].replace('BMO', '8:00:00')
        thedf['bmoamc'] = thedf['bmoamc'].replace('AMC', '16:00:00')
        thedf['Earnings Date'] = thedf['Earnings Date'].astype(str) + ' ' + thedf['bmoamc'].astype(str)
        thedf['Earnings Date'] = thedf['Earnings Date']
        thedf = thedf.drop(columns=['bmoamc'])
        thedf = thedf.rename(columns={'Symbol': 'ticker', 'Avg Option Volume': 'averageoptionvol', 'Earnings Date': 'exactearningsdate', 'Name': 'companyname', 'Avg. Stock Volume': 'averagestockvol', 'MarketCap': 'marketcap'}, errors='raise')
        thedf.drop(thedf.columns[0], axis = 1)
        
        return render_template('upload.html', tables=[thedf.to_html()], titles=[''])
    return render_template('upload.html')

@app.route('/importit', methods=['GET', 'POST'])
def importit():
    thedf.to_sql('earningsdates', con=db.engine, if_exists='append', index=False)
    success = str('Success')
    return render_template('import.html', tables=[thedf.to_html()], titles=[''], success=success)
