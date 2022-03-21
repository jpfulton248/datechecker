from tokenize import group
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from collections import OrderedDict, defaultdict
import json
from itertools import groupby
from pyparsing import col

mylist = ([{"exactearningsdatestr":"3/20/22","time":"Before Market Open","ticker":"AAPL"},
{"exactearningsdatestr":"3/20/22","time":"Before Market Open","ticker":"GME"},
{"exactearningsdatestr":"3/20/22","time":"After Market Close","ticker":"F"},
{"exactearningsdatestr":"3/20/22","time":"After Market Close","ticker":"DOC"},
{"exactearningsdatestr":"3/21/22","time":"Before Market Open","ticker":"WMT"},
{"exactearningsdatestr":"3/21/22","time":"Before Market Open","ticker":"FB"},
{"exactearningsdatestr":"3/21/22","time":"After Market Close","ticker":"NFLX"},
{"exactearningsdatestr":"3/21/22","time":"After Market Close","ticker":"GOOGL"},
{"exactearningsdatestr":"3/22/22","time":"Before Market Open","ticker":"ABNB"},
{"exactearningsdatestr":"3/22/22","time":"Before Market Open","ticker":"VALE"},
{"exactearningsdatestr":"3/22/22","time":"Before Market Open","ticker":"NKE"},
{"exactearningsdatestr":"3/22/22","time":"After Market Close","ticker":"ADBE"},
{"exactearningsdatestr":"3/23/22","time":"Before Market Open","ticker":"PTON"},
{"exactearningsdatestr":"3/23/22","time":"Before Market Open","ticker":"BBY"},
{"exactearningsdatestr":"3/23/22","time":"Before Market Open","ticker":"BBW"},
{"exactearningsdatestr":"3/23/22","time":"After Market Close","ticker":"HPQ"},
{"exactearningsdatestr":"3/23/22","time":"After Market Close","ticker":"WDAY"},
{"exactearningsdatestr":"3/23/22","time":"After Market Close","ticker":"ZM"}])

df = pd.DataFrame(mylist)

dict_ = df.to_dict(orient='rows')

lists = {}

for k, g in groupby(dict_, key=lambda t: t['title']):
    lists[k] = list(g)

for list_, items in lists.items():
    print(list_)
    for item in items:
        print('    ', item['content'])


# print(mylist)

# for k, g in groupby(mylist, key=lambda e: e['exactearningsdatestr']):
#     lists[k] = list(g)

# for list_, items in lists.items():
#     print(list_)
#     for item in items:
#         print('    ', item['ticker'])