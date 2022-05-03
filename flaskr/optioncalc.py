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
from .myfunx import calcabsavg, genbefaf, histurl, getcurrent, getiv, now, yesterday, fourhrsago, screenerend
import requests
from .bs import straddlebe, straddle

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
    expiry = db.Column(db.String())
    updated = db.Column(db.String())


def straddlebe(spot, strike, dte, ivcrushed, optprice, paid):

    def breakevenup(spot, strike, dte, ivcrushed, optprice, paid):
        breakeven = 1
        while breakeven > 0:
            spot += .05
            strad = straddle(spot, strike, dte, ivcrushed, optprice)
            breakeven = paid - strad
            beup = spot
            return beup

    def breakevendown(spot, strike, dte, ivcrushed, optprice, paid):
        breakeven = -1
        while breakeven < 0:
            spot -= .05
            strad = straddle(spot, strike, dte, ivcrushed, optprice)
            breakeven = paid - strad
            bedown = spot
            return bedown
    bedown = breakevendown(spot, strike, dte, ivcrushed, optprice, paid)
    beup = breakevenup(spot, strike, dte, ivcrushed, optprice, paid)
    return bedown, beup

def calcbe(spot, strike, dte, ivcrushed, optprice, ticker):
    s = Screener.query.with_entities(Screener.underlyingprice, Screener.strike, Screener.straddlemid, Screener.ivcrushto, Screener.exactearningsdate, Screener.expiry).filter(Screener.ticker == ticker).all()