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
from .myfunx import genbefaf, histurl, getcurrent, getiv
import requests

from pymysql import NULL
load_dotenv
# USERNAME = os.environ.get('USERNAME')
# HOST = os.environ.get('HOST')
# DATABASE = os.environ.get('DATABASE')
# PASSWORD = os.environ.get('PASSWORD')
# PORT = os.environ.get('PORT')
#production
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

class Screener(db.Model):
    screenerid = db.Column(db.Integer(), primary_key=True)
    ticker = db.Column(db.String(255))
    tickerlink = db.Column(db.String(255))
    companyname = db.Column(db.String(255))
    averageoptionvol = db.Column(db.String(255))
    averagestockvol = db.Column(db.String(255))
    marketcap = db.Column(db.String(255))
    iv = db.Column(db.Numeric(10,2))
    straddlemid = db.Column(db.Numeric(20,2))
    impliedmove = db.Column(db.Numeric(10,2))
    histavg = db.Column(db.Numeric(10,5))
    underlyingprice = db.Column(db.Numeric(20,2))
    strike = db.Column(db.Numeric(20,2))
    valued = db.Column(db.Numeric(20,5))
    ivcrushto = db.Column(db.Numeric(20,2))
    exactearningsdate = db.Column(db.String())
    edate = db.Column(db.String())
    etime = db.Column(db.String())
    updated = db.Column(db.String())

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
        print('changes table failed')
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
    if df.empty == True:
        print('historical df empty on', routeticker)
        cumabsavgperc = 0
        countreports = 0
        return cumabsavgperc, countreports
    else:
        df = df.sort_values(['EarningsDate'], ascending=[False])
        #line below can be used to limit history
        df = df.head(48)
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
        underover = 1
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

def computescreener():
    s = Screener.query.with_entities(Screener.ticker, Screener.companyname, Screener.averageoptionvol, Screener.averagestockvol, Screener.marketcap, Screener.iv, Screener.straddlemid, Screener.impliedmove, Screener.histavg, Screener.underlyingprice, Screener.strike, Screener.valued, Screener.ivcrushto, Screener.edate, Screener.etime, Screener.exactearningsdate).all()
    df = pd.DataFrame(s)
    if df.empty == False:
        df = df.sort_values(['exactearningsdate'], ascending=[True])
        df = df.drop(columns=['exactearningsdate'])
        df['iv'] = df['iv'].astype(str) + '%'
        df['straddlemid'] = '$' + df['straddlemid'].astype(str)
        df['impliedmove'] = df['impliedmove'].astype(str) + '%'
        df['histavg'] = df['histavg'].astype(str) + '%'
        df['underlyingprice'] = '$' + df['underlyingprice'].astype(str)
        df['strike'] = '$' + df['strike'].astype(str)
        df['ticker'] = '<a href="' + df['ticker'].astype(str) + '" style="color:#FFFFFF;">' + df['ticker'].astype(str) + '</a>'
        pd.options.display.float_format = '{:,}'.format 
        pd.options.display.float_format = '{:,.0f}'.format
    computedscreenerdf = df
    return computedscreenerdf

@app.route('/')
def screener():
    computedscreenerdf = computescreener()
    computedscreenerdf.to_csv('flaskr/static/screener.csv', index='False')
    return render_template('screener.html', screener=computedscreenerdf.to_html(classes='table table-dark sortable table-striped', table_id='sortit', escape=False, index=False, header=True, render_links=True, justify='left'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global thedf
    if request.method == 'POST':
        file = request.files['file']        
        thedf = pd.read_csv(file)
        foredatesdf, forscreenerdf = prepimport()
        these = Screener.query.all()
        db.session.query(Screener).delete()
        db.session.commit()
        forscreenerdf.to_sql('screener', con=db.engine, if_exists='append', index=False)    
        foredatesdf.to_sql('earningsdates', con=db.engine, if_exists='append', index=False) 
        return render_template('upload.html')
    return render_template('upload.html')

def prepimport():
    thedfprepped = thedf
    thedfprepped.reset_index
    thedfprepped['Name'] = thedfprepped['Name'].str[:40]
    thedfprepped = thedfprepped.drop(columns=['Implied Move', 'Implied Move Relative to 4-Qtr Avg', 'Implied Move Relative to 12-Qtr Avg', 'Implied Move Relative to 12-Qtr Median', 'Abs. Avg Implied Move', 'Abs. Avg Actual Move', 'Abs. Max Actual Move', 'Abs. Min Actual Move', 'Abs. Avg Implied Move.1', 'Abs. Avg Actual Move.1', 'Abs. Median Actual Move', 'Abs. Max Actual Move.1', 'Abs. Min Actual Move.1', 'Current Price', 'InWatchlist', 'EtfHoldingsList', 'Sector', 'Industry', 'Diff_ImpliedVsLast4AvgImplied', 'Diff_ImpliedVsLast12AvgImplied'])
    thedfprepped[['beforedate', 'afterdate']] = '',''
    thedfprepped[['edate2', 'bmoamc2']] = thedfprepped[['Earnings Date', 'bmoamc']]
    thedfprepped['Earnings Date'] = pd.to_datetime(thedfprepped['Earnings Date'])
    thedfprepped['bmoamc'] = thedfprepped['bmoamc'].replace('BMO', '8:00:00')
    thedfprepped['bmoamc'] = thedfprepped['bmoamc'].replace('AMC', '16:00:00')
    thedfprepped['Earnings Date'] = thedfprepped['Earnings Date'].astype(str) + ' ' + thedfprepped['bmoamc'].astype(str)
    thedfprepped[['expiry', 'strike', 'iv', 'straddlemid', 'impliedmove', 'underlyingprice', 'histavg', 'cntreports', 'ivcrushto', 'valued']] = '','','','','','','','','',''
    i = len(thedfprepped.index) + 1
    for index, row in thedfprepped.iterrows():
        i -= 1
        targetdate = row['Earnings Date']
        targetdate = datetime.datetime.strptime(targetdate, '%Y-%m-%d %H:%M:%S')
        theticker = row['Symbol']
        beforedate, afterdate = genbefaf(targetdate)
        thedfprepped.at[index, 'beforedate'] = beforedate
        thedfprepped.at[index, 'afterdate'] = afterdate
        print('getting before/after dates', i)
    i = len(thedfprepped.index) + 1
    for index, row in thedfprepped.iterrows():
        i -= 1
        targetdate = row['Earnings Date']
        theticker = row['Symbol']
        expiry, strike, iv, straddlemid, impliedmove, underlyingprice = getcurrent(theticker, row['beforedate'])
        thedfprepped.at[index, 'expiry'] = expiry
        thedfprepped.at[index, 'strike'] = strike
        thedfprepped.at[index, 'iv'] = iv
        thedfprepped.at[index, 'straddlemid'] = straddlemid
        thedfprepped.at[index, 'impliedmove'] = impliedmove
        thedfprepped.at[index, 'underlyingprice'] = underlyingprice
        print('getting option chain', i)
    i = len(thedfprepped.index) + 1
    for index, row in thedfprepped.iterrows():
        i -= 1
        cumabsavgperc, countreports = historical(row['Symbol'])
        thedfprepped.at[index, 'histavg'] = cumabsavgperc
        thedfprepped.at[index, 'cntreports'] = countreports
        print('getting historical', i)
    i = len(thedfprepped.index) + 1
    for index, row in thedfprepped.iterrows():
        i -= 1
        thedfprepped.at[index, 'ivcrushto'] = getiv(row['Symbol'])
        print('getting iv crush', i)

    #df for importing into exactearningsdates
    foredatesdf = thedfprepped.rename(columns={'Symbol': 'ticker', 'Avg Option Volume': 'averageoptionvol', 'Earnings Date': 'exactearningsdate', 'Name': 'companyname', 'Avg. Stock Volume': 'averagestockvol', 'MarketCap': 'marketcap', 'histavg': 'actualmoveperc', 'iv': 'staticiv', 'expiry': 'staticexpiry'}, errors='raise')
    foredatesdf = foredatesdf[['ticker', 'companyname', 'exactearningsdate', 'beforedate', 'afterdate','averageoptionvol', 'averagestockvol', 'marketcap', 'impliedmove', 'staticexpiry']]

    #df for importing into screener
    forscreenerdf = thedfprepped[['Symbol', 'Name', 'Avg Option Volume', 'Avg. Stock Volume', 'MarketCap', 'iv', 'straddlemid', 'impliedmove', 'histavg', 'underlyingprice', 'strike', 'valued', 'edate2', 'bmoamc2', 'Earnings Date', 'ivcrushto']]
    forscreenerdf = forscreenerdf.rename(columns={'Symbol': 'ticker', 'edate2': 'edate', 'bmoamc2': 'bmoamc', 'Name': 'companyname', 'Avg Option Volume': 'averageoptionvol', 'Avg. Stock Volume': 'averagestockvol', 'MarketCap': 'marketcap', 'Earnings Date': 'exactearningsdate', 'bmoamc2': 'etime'}, errors='raise')
    forscreenerdf['valued'] = forscreenerdf['impliedmove'] - forscreenerdf['histavg']
    forscreenerdf['marketcap'] = forscreenerdf['marketcap'].div(1000000000)
    forscreenerdf = forscreenerdf.sort_values(['exactearningsdate'], ascending=[True])
    return foredatesdf, forscreenerdf
