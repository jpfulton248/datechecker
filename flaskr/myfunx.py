import datetime
from dotenv import load_dotenv
import os
load_dotenv

f_api_key = os.environ.get('f_api_key')


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