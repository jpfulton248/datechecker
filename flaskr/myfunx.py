import datetime
from dotenv import load_dotenv
import os
import time
from tda import auth, client
import mysql.connector as mysql
import pandas as pd
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
    print('getting option chain for', ticker)
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
    time.sleep(.4)
    expiry = list(r.json()["putExpDateMap"])[0]
    print(expiry)
    strike = list(r.json()["putExpDateMap"][expiry])[0]
    callbid = r.json()["callExpDateMap"][expiry][strike][0]["bid"]
    callask = r.json()["callExpDateMap"][expiry][strike][0]["ask"]
    try:
        callmid = (callbid + callask)/2
        callmid = round(callmid,2)
    except:
        callmid = 0
    # callspread = round(((1-(callbid/callask))*100), 2)
    putbid = r.json()["putExpDateMap"][expiry][strike][0]["bid"]
    putask = r.json()["putExpDateMap"][expiry][strike][0]["ask"]
    try:
        putmid = (putbid + putask)/2
        putmid = round(putmid,2)
    except:
        putmid = 0
    # putspread = round(((1-(putbid/putask))*100), 2)

    #this is IV of the ATM call option for expiration immediately following next earnings date
    try:
        ivc = round(r.json()["callExpDateMap"][expiry][strike][0]["volatility"], 2)
    except:
        ivc = 0
    try:
        ivp = round(r.json()["putExpDateMap"][expiry][strike][0]["volatility"], 2)
    except:
        ivp = 0
    
    try:
        iv = ((ivc + ivp)/2)
    except:
        iv = 0

    #price of the underlying here... I've seen bad data come from TD for this which sucks.
    try:
        underlyingprice = r.json()["underlyingPrice"]
        underlyingprice = round(underlyingprice, 2)
    except:
        underlyingprice = 0

    #mid price of straddle. Using mid vs last since some tickers can have very little volume. At least this will provide more data. Might change to last.
    try:
        straddlemid = round(putmid+callmid, 2)
    except:
        straddlemid = 0

    #calculate implied move
    try:
        impliedmove = ((straddlemid/underlyingprice)*100)
        impliedmove = round(impliedmove, 2)
    except:
        impliedmove = 0

    #make the exipration date more human readable
    prettyexpiry = expiry.split(':')[0]
    prettyexpiry = datetime.datetime.strptime(prettyexpiry, '%Y-%m-%d')
    prettyexpiry = datetime.datetime.strftime(prettyexpiry, '%Y-%m-%d')
    currentchain = []
    currentchain = prettyexpiry, strike, iv, straddlemid, impliedmove, underlyingprice
    # except:
    #     print('problem getting option chain so currentchain is blank')

    return currentchain

def getiv(theticker):
#this gets the date 90 days from today. I reference later with futuredate.year, futuredate.month, futuredate.day
    futuredate = datetime.date.today() + datetime.timedelta(days=150)
    # try:
    r = c.get_option_chain(theticker,
    contract_type=None,
    strike_count=1,
    include_quotes=None,
    strategy=client.Client.Options.Strategy.ANALYTICAL,
    interval=None,
    strike=None,
    strike_range=None,
    from_date=datetime.date(year=datetime.date.today().year, month=datetime.date.today().month, day=datetime.date.today().day),
    to_date=datetime.date(year=futuredate.year, month=futuredate.month, day=futuredate.day),
    volatility=None,
    underlying_price=None,
    interest_rate=None,
    days_to_expiration=None,
    exp_month=None,
    option_type=None)
    assert r.status_code == 200, r.raise_for_status()
    exptier = list(r.json()["putExpDateMap"])
    df2 = pd.DataFrame(exptier, columns=['expirykey'])
    df2['expirys'] = df2['expirykey'].str.slice(start=0, stop=10)
    mydict = {"Ticker":[],"Expiration":[],"IV":[],"Strike":[]}
    for index, row in df2.iterrows():
        strike = list(r.json()["putExpDateMap"][row['expirykey']])[0]
        ivc = round(r.json()["callExpDateMap"][row['expirykey']][strike][0]["volatility"], 2)
        ivp = round(r.json()["putExpDateMap"][row['expirykey']][strike][0]["volatility"], 2)
        iv = ((ivc + ivp)/2)
        mydict["IV"].append(iv)
        mydict["Expiration"].append(row['expirys'])
        mydict["Ticker"].append(theticker)
        mydict["Strike"].append(strike)
    df3 = pd.DataFrame.from_dict(mydict)
    df3.reset_index(drop=True, inplace=True)
    if (datetime.datetime.strptime(df3.loc[1,'Expiration'], '%Y-%m-%d') - datetime.datetime.strptime(df3.loc[0,'Expiration'], '%Y-%m-%d')).days >= 14:
        ivcrushto = df3.at[2, 'IV']
    elif (datetime.datetime.strptime(df3.loc[1,'Expiration'], '%Y-%m-%d') - datetime.datetime.strptime(df3.loc[0,'Expiration'], '%Y-%m-%d')).days < 14:
        ivcrushto = df3.at[5, 'IV']
    else:
        print('Expirations are neither greater than 14, or less than 14 days apart')
        ivcrushto = 0
        pass
    if ivcrushto == -999:
        ivcrushto = 0
    time.sleep(.5)
    return ivcrushto

    