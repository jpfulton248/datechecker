from flaskr.mm import app
from dotenv import load_dotenv
import os
load_dotenv
SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
 

if __name__ == "__mm__":
        app.run()
