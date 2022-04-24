import datetime
from dotenv import load_dotenv
import os
import time
from tda import auth, client
import mysql.connector as mysql
load_dotenv

f_api_key = os.environ.get('f_api_key')
tdapi_key = os.environ.get('api_key')
redirect_uri = os.environ.get('redirect_uri')
token_path = os.environ.get('token_path')

try:
    c = auth.client_from_token_file(token_path, tdapi_key)
except mysql.connector.FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome() as driver:
        c = auth.client_from_login_flow(
            driver, tdapi_key, redirect_uri, token_path)



# THESE ARE FUNCTIONS I'VE MADE THAT COULD BE REUSED

#convert to HH-MM-SS string
def to_ymds(adate):
    adate = datetime.datetime.strftime(adate, "%Y-%m-%d")
    return adate

#convert to HH-MM-SS datetime
def to_ymdd(adate):
    adate = datetime.datetime.strptime(adate, "%Y-%m-%d")
    return adate

#generate the date date of target minus 1 and the date of target plus 1 depending on hour and avoid weekends
def genbefaf(targetdate):
    thetime = str(datetime.datetime.strftime(targetdate, "%-H"))
    if thetime == "8":
        #if target date's time is 8am, before date is minus 1 then convert to str YYYY-MM-DD
        beforedate = to_ymds(targetdate - datetime.timedelta(days=1))
        #if target date's time is 8am (before market open), after date is same date as exact earnings but switch to string in YYYY-MM-DD
        afterdate = to_ymds(targetdate)
    elif thetime == "16":
        #if target date's time is 4pm, before date is same as earningsdate but then convert format to str YYYY-MM-DD
        beforedate = to_ymds(targetdate)
        #if target date's time is 4pm, before date is minus 1 then convert to str YYYY-MM-DD
        afterdate = to_ymds(targetdate + datetime.timedelta(days=1))
    else:
        beforedate = "ERROR calculating before date on " + to_ymds(targetdate)
        afterdate = "ERROR calculating after date"
    #change before date to Friday if it was originally Sunday
    if datetime.datetime.weekday(to_ymdd(beforedate)) == 6:
        beforedate = to_ymds(to_ymdd(beforedate) - datetime.timedelta(days=2))
    #change after date to Monday if it was originally Saturday
    if datetime.datetime.weekday(to_ymdd(afterdate)) == 5:
        afterdate = to_ymds(to_ymdd(afterdate) + datetime.timedelta(days=2))    
    return beforedate, afterdate

def histurl(histticker, fromdate, todate):
    #assign variables for request url api
    first = "https://financialmodelingprep.com/api/v3/historical-price-full/"
    from_ = "?from="
    to_ = "&to="
    key = "&apikey="
    urlthing = str(first)+str(histticker)+str(from_)+str(fromdate)+str(to_)+str(todate)+str(key)+str(f_api_key)
    return urlthing

def getcurrent(ticker, beforedate):
    beforedate = datetime.datetime.strptime(beforedate, "%Y-%m-%d")
    beforedate40 = beforedate + datetime.timedelta(days=40)
    r = c.get_option_chain(ticker,
    contract_type=None,
    strike_count=1,
    include_quotes=None,
    strategy=client.Client.Options.Strategy.ANALYTICAL,
    interval=None,
    strike=None,
    strike_range=None,
    from_date=datetime.date(year=beforedate.year, month=beforedate.month, day=beforedate.day),
    to_date=datetime.date(year=beforedate40.year, month=beforedate40.month, day=beforedate40.day),
    volatility=None,
    underlying_price=None,
    interest_rate=None,
    days_to_expiration=None,
    exp_month=None,
    option_type=None)
    assert r.status_code == 200, r.raise_for_status()
    time.sleep(1)
    try:
        expiry = list(r.json()["putExpDateMap"])[0]
        strike = list(r.json()["putExpDateMap"][expiry])[0]
        callbid = r.json()["callExpDateMap"][expiry][strike][0]["bid"]
        callask = r.json()["callExpDateMap"][expiry][strike][0]["ask"]
        callmid = (callbid + callask)/2
        callmid = round(callmid,2)
        # callspread = round(((1-(callbid/callask))*100), 2)
        putbid = r.json()["putExpDateMap"][expiry][strike][0]["bid"]
        putask = r.json()["putExpDateMap"][expiry][strike][0]["ask"]
        putmid = (putbid + putask)/2
        putmid = round(putmid,2)
        # putspread = round(((1-(putbid/putask))*100), 2)

        #this is IV of the ATM call option for expiration immediately following next earnings date
        ivc = round(r.json()["callExpDateMap"][expiry][strike][0]["volatility"], 2)
        ivp = round(r.json()["putExpDateMap"][expiry][strike][0]["volatility"], 2)
        iv = ((ivc + ivp)/2)

        #price of the underlying here... I've seen bad data come from TD for this which sucks.
        underlyingprice = r.json()["underlyingPrice"]
        underlyingprice = round(underlyingprice, 2)

        #mid price of straddle. Using mid vs last since some tickers can have very little volume. At least this will provide more data. Might change to last.
        straddlemid = round(putmid+callmid, 2)

        #calculate implied move
        impliedmove = ((straddlemid/underlyingprice)*100)
        impliedmove = round(impliedmove, 2)

        #make the exipration date more human readable
        prettyexpiry = expiry.split(':')[0]
        prettyexpiry = datetime.datetime.strptime(prettyexpiry, '%Y-%m-%d')
        prettyexpiry = datetime.datetime.strftime(prettyexpiry, '%Y-%m-%d')
        currentchain = []
        currentchain = prettyexpiry, strike, iv, straddlemid, impliedmove, underlyingprice
    except:
        print('problem getting option chain so currentchain is blank')
    return currentchain