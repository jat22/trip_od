import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
BASE_URL = os.getenv("BASE_URL")
WTF_CSRF_SECRET_KEY = os.getenv("WTF_CRSF_SECRET_KEY")
