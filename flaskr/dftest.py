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

class spy(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    price = db.Column(db.Numeric(20,2))
    volume = db.Column(db.Integer())
    high = db.Column(db.Numeric(20,2))
    low = db.Column(db.Numeric(20,2))
    open = db.Column(db.Numeric(20,2))
    dated = db.Column(db.String())

class indexes(db.Model):
    indexesid = db.Column(db.Integer(), primary_key=True)
    symbol = db.Column(db.String())
    price = db.Column(db.Numeric(20,2))
    percchange = db.Column(db.Numeric(4,2))
    change = db.Column(db.Numeric(10,2))
    daylow = db.Column(db.Numeric(20,2))
    dayhigh = db.Column(db.Numeric(20,2))
    volume = db.Column(db.Integer())
    avgvol = db.Column(db.Integer())
    open = db.Column(db.Numeric(20,2))
    prevclose = db.Column(db.Numeric(20,2))
    dated = db.Column(db.String())


@app.route('/dftest')
def dftest():
    symbol = 'AAPL'
    result = Main.query.join(earningsdates, Main.ticker==earningsdates.ticker).filter(Main.ticker==symbol).first()
    return render_template('dftest.html',
        result=result) 