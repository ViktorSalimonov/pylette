import os

class Config():
    DEBUG = False
    TESTING = False
    UPLOAD_FOLDER = '/home/salv/Projects/qkr/data'
    ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True


