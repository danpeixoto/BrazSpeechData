import random
import string
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()




class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    salt = db.Column(db.String(100))
    last_login_time = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))

class Dataset(db.Model):
    __tablename__ = 'Dataset'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000))
    audio_lenght = db.Column(db.Integer())
    file_path= db.Column(db.String(250), unique=True)
    file_with_user = db.Column(db.Integer()) # true if 
    user_validated = db.Column(db.String(100))
    instance_validated = db.Column(db.Integer()) #1 if human validated this instance
    instance_valid = db.Column(db.Integer())# 1 if instance is ok
    


