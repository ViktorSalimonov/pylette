import os

class Config():
    DEBUG = False
    TESTING = False
    ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
    

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    UPLOAD_FOLDER = '/home/salv/Projects/qkr/data'
    POSTGRES = {
    'user': 'postgres',
    'pw': '',
    'db': 'qkr',
    'host': 'localhost',
    'port': '5432',
    }
    