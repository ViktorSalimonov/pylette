import os

class Config():
    DEBUG = False
    TESTING = False
    ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
    

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    UPLOAD_FOLDER = '/home/salv/Projects/qkr/data'
    CELERY_BROKER_URL = 'ampq://localhost//'
    SQLALCHEMY_DATABASE_URI = #to-do


