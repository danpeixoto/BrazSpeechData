# coding: utf-8
import random
import string
import json

class Config:
    SECRET_KEY = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(60))
    with open('./common/enviroment.json') as json_file:
        DATABASE_CONNECTION_STRING = json.load(json_file)['db']
    SQLALCHEMY_DATABASE_URI = 'mysql://utf:speechbraz@localhost/braz'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}
