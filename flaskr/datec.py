from flask import Flask, current_app, jsonify, render_template, url_for, redirect, request, Response, escape, abort
from flask_sqlalchemy import SQLAlchemy
from matplotlib import image
from numpy import logical_or
import datetime
import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import false, true
import io

load_dotenv

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
f_api_key = os.environ.get('f_api_key')

app=Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI
db=SQLAlchemy(app)


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
                try:
                    str.upper(bmoamc)
                except:
                    pass
                if projected != 1:
                    if kedate == edate and bmoamc == kbmoamc and bmoamc != 'None':
                        issues = str('No Issues')
                        forfilter = str('Include')
                    if kedate == edate and bmoamc == 'None':
                        issues = str('Date is Correct. Time unknown.')
                        forfilter = str('Include')
                    if kedate != edate and bmoamc == kbmoamc and edate != 'None':
                        issues = str('Date has been corrected. Time is Correct')
                        forfilter = str('Include')
                    if kedate == edate and bmoamc != kbmoamc and bmoamc != 'None':
                        issues = str('Date is Correct. Time has been corrected.')
                    if kedate != edate and bmoamc != kbmoamc and edate != '':
                        issues = str('Date and time have both been corrected')
                        forfilter = str('Include')
                else:
                    issues = str('Projected. Not Confirmed.')
                    forfilter = str('Exclude')
            else:
                issues = str('Date not found. Earnings date likely not announced.')
                forfilter = str('Exclude')
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
        issuesdf.to_csv('flaskr/static/issues.txt', index=False, header=None, columns=['ticker', 'correct_date'])
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