import os

class Config():
    DEBUG = False
    TESTING = False
    ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
    LOGFILE = '/home/salv/Projects/qkr/app/app.log'

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    UPLOAD_FOLDER = '/home/salv/Projects/qkr/uploads'
    RESULT_FOLDER = '/home/salv/Projects/qkr/results'
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
    POSTGRES = {
    'user': 'postgres',
    'pw': '',
    'db': 'qkr',
    'host': 'localhost',
    'port': '5432',
    }
    