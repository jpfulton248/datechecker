from flaskr.mm import app
from dotenv import load_dotenv
import os
load_dotenv
USERNAME = os.environ.get('USERNAME')
HOST = os.environ.get('HOST')
DATABASE = os.environ.get('DATABASE')
PASSWORD = os.environ.get('PASSWORD')
PORT = os.environ.get('PORT')
SQLALCHEMY_DATABASE_URI=str('mysql+pymysql://') + USERNAME + str(':') + PASSWORD + str('@') + HOST + str(':') + PORT + str('/') + DATABASE
 

if __name__ == "__mm__":
        app.run()
