from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from config import sqlalchemyurl
import datetime
import pandas as pd
from markupsafe import Markup

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemyurl
db = SQLAlchemy(app)

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
    exactearningsdate = db.Column(db.String())

@app.route('/<string:ticker>')
def hello(ticker):
    theticker =  Main.query.filter_by(ticker = ticker).first()
    companyname = theticker.company_name
    avg_optvol = theticker.avg_optvol
    market_cap = theticker.market_cap
    avg_stockvol = theticker.avg_stockvol
    theticker = theticker.ticker
    edate = earningsdates.query.filter_by(ticker = ticker).first()
    exactearningsdate = edate.exactearningsdate
    thisticker = edate.ticker
    now = datetime.datetime.now()
    #condition = earningsdates.exactearningsdate > now
    sidebar = earningsdates.query \
        .with_entities(earningsdates.ticker, earningsdates.exactearningsdate) \
        .filter(earningsdates.exactearningsdate > now).all()
    df = pd.DataFrame (sidebar, columns =['ticker', 'exactearningsdate'])
    df['ticker'] = '<a href="' + df.ticker.map(str) + '">'  + df.ticker.map(str) + '</a>'


    return render_template('index.html', 
        theticker=thisticker,
        companyname = companyname,
        avg_optvol = avg_optvol,
        market_cap = market_cap,
        avg_stockvol = avg_stockvol,
        earningsdate = exactearningsdate,
        thedate = now,
        tables = df.to_html(classes='table table-dark sidebarhref', border=None, render_links=True, escape=False, index=False, header=False))
        