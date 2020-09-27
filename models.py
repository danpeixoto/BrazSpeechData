# coding: utf-8
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
    file_path= db.Column(db.String(250), unique=False)# Alterar aqui depois de resolver o problema do sp
    file_with_user = db.Column(db.Integer()) # true if 
    user_validated = db.Column(db.String(200))
    user_validated2 = db.Column(db.String(200))
    user_validated3 = db.Column(db.String(200))
    instance_validated = db.Column(db.Integer()) #1 if human validated this instance
    instance_valid = db.Column(db.Integer())# 1 if instance is ok
    number_validated = db.Column(db.Integer()) # Number of validations
    type_valid_1 = db.Column(db.Integer()) # 1 if instance was validated by this type
    type_valid_2 = db.Column(db.Integer()) # 1 if instance was validated by this type
    type_valid_3 = db.Column(db.Integer()) # 1 if instance was validated by this type
    type_valid_4 = db.Column(db.Integer()) # 1 if instance was validated by this type
    type_valid_5 = db.Column(db.Integer()) # 1 if instance was validated by this type
    type_valid_6 = db.Column(db.Integer()) # 1 if instance was validated by this type
    data_gold = db.Column(db.Integer()) # Verificar se o dataset é gold ou nao
    invalid_reason = db.Column(db.String(2000))

class TimeValidated(db.Model):
    __tablename__ = 'TimeValidated'
    id = db.Column(db.Integer, primary_key=True)
    user_validated = db.Column(db.String(100))
    id_data = db.Column(db.Integer)
    time_validated = db.Column(db.DateTime())
    


