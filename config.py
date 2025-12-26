import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    DEBUG = True
    JSON_SORT_KEYS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'planner.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False