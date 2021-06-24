import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
WTF_CSRF_ENABLED = False
# Enable debug mode.
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
# Connect to the database
SECRET_KEY = os.urandom(32)

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI =  'postgresql://postgres:1234@localhost:5432/fyyur_02'
