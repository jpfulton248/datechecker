#!/Users/jpfulton/dc/myenv/bin/python
from random import randint
from site import setcopyright
from ssl import ALERT_DESCRIPTION_ACCESS_DENIED, CHANNEL_BINDING_TYPES
from token import EXACT_TOKEN_TYPES
from flask import Flask, current_app, render_template, url_for, redirect, request, Response, escape, abort
from flask_sqlalchemy import SQLAlchemy
from matplotlib import image
from numpy import logical_or
import datetime
import pandas as pd
from markupsafe import Markup
import re
from dotenv import load_dotenv
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from sqlalchemy import false, true
import requests
import io
import markdown
from functools import wraps
import asyncio
import pyperclip as pc
import asyncio
from pymysql import NULL
from aiohttp import ClientSession
import aiohttp
import ssl
import certifi
from subprocess import Popen, PIPE, STDOUT
import time
import sys



load_dotenv

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
#local
# SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI_DEBUG')
f_api_key = os.environ.get('f_api_key')
# SQLALCHEMY_DATABASE_URI=str('mysql+pymysql://') + USERNAME + str(':') + PASSWORD + str('@') + HOST + str(':') + PORT + str('/') + DATABASE
i = 1
old_stdout = sys.stdout



while i < 2000:
    log_file = open("flaskr/testit.log","w")
    sys.stdout = log_file
    i += 1
    print(randint(500,2000))
    log_file.close()
    time.sleep(1)



sys.stdout = old_stdout