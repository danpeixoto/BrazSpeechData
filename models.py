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
    carga_horaria = db.Column(db.Integer)
    data_inicio = db.Column(db.String(100))
    data_fim = db.Column(db.String(100))


class Dataset(db.Model):
    __tablename__ = 'Dataset'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text())
    audio_lenght = db.Column(db.Integer())
    # Alterar aqui depois de resolver o problema do sp
    file_path = db.Column(db.String(250), unique=False)
    file_with_user = db.Column(db.Integer())  # true if
    user_validated = db.Column(db.String(200))
    user_validated2 = db.Column(db.String(200))
    user_validated3 = db.Column(db.String(200))
    # 1 if human validated this instance
    instance_validated = db.Column(db.Integer())
    number_validated = db.Column(db.Integer())  # Number of validations
    # classe invalida definida pelo usuario (-1 -> -7)
    invalid_user1 = db.Column(db.Integer())
    # classe invalida definida pelo usuario (-1 -> -7)
    invalid_user2 = db.Column(db.Integer())
    # classe invalida definida pelo usuario (-1 -> -7)
    invalid_user3 = db.Column(db.Integer())
    # classes validas definida pelo usuario (lista de valores transformada em string)
    valids_user1 = db.Column(db.String(200))
    # classes validas definida pelo usuario (lista de valores transformada em string)
    valids_user2 = db.Column(db.String(200))
    # classes validas definida pelo usuario (lista de valores transformada em string)
    valids_user3 = db.Column(db.String(200))
    data_gold = db.Column(db.Integer())  # Verificar se o dataset é gold ou nao
    invalid_reason1 = db.Column(db.String(2000))  # rasão invalida
    invalid_reason2 = db.Column(db.String(2000))  # rasão invalida
    invalid_reason3 = db.Column(db.String(2000))  # rasão invalida
    duration = db.Column(db.Integer())  # Time of the audio
    # Control for that only one receive the path, SETAR COMO 0 POR PADRAO
    travado = db.Column(db.DateTime())
    # 0 para anotar e 1 para transcrever, valor padrão é 0
    task = db.Column(db.Integer())
    # Text fornecido pelo ASR, o que será transcrito fica em TEXT
    text_asr = db.Column(db.Text())
    CER = db.Column(db.Float())


class TimeValidated(db.Model):
    __tablename__ = 'TimeValidated'
    id = db.Column(db.Integer, primary_key=True)
    user_validated = db.Column(db.String(100))
    id_data = db.Column(db.Integer)
    time_validated = db.Column(db.DateTime())
    duration = db.Column(db.Integer)
    answer = db.Column(db.Text())
