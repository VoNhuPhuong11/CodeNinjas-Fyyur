import os
from sqlalchemy import create_engine
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgresql://phuongvn3:123@localhost:5432/codeninjas'

engine = create_engine(SQLALCHEMY_DATABASE_URI)

try:
    connection = engine.connect()
    print('Kết nối đến cơ sở dữ liệu thành công!')
except:
    print('Không thể kết nối đến cơ sở dữ liệu.')
