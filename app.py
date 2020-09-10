
import random
import string
import hashlib
from functools import wraps
import datetime
import os
import shutil
import tempfile

from flask import Flask
from flask_script import Manager

from models import db, Dataset
from webui import webui
#from api import api
from config import config


# csv data from make dataset
data_csv = 'static/Dataset/metadata.csv'
data_validated_csv = 'static/Dataset/metadata_validated.csv'

app = Flask(__name__)
app.config.from_object(config['dev'])
app.register_blueprint(webui)
#app.register_blueprint(api, url_prefix="/api")
db.init_app(app)
manager = Manager(app)


@app.after_request
def headers(response):
    response.headers["Server"] = "Audio-Validation"
    return response


@manager.command
def initdb():
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def initdataset():
    lines = list(open(data_csv).readlines())

    for line in lines:
        audio_path,lenght,text = line.split(',')
        text = text.replace('\n','')
        new_data= Dataset()
        new_data.text = text
        new_data.audio_lenght = lenght
        new_data.file_path= audio_path
        new_data.file_with_user = 0 # 1 if user validating this instance
        new_data.instance_validated = 0 #1 if human validated this instance
        new_data.user_validated = ''
        new_data.instance_valid = 0 # 1 if instance is ok
        db.session.add(new_data)
    db.session.commit()


@manager.command
def initvalidateddataset():
    lines = list(open(data_validated_csv).readlines())

    for line in lines:
        audio_path,lenght,text = line.split(',')
        text = text.replace('\n','')
        new_data= Dataset()
        new_data.text = text
        new_data.audio_lenght = lenght
        new_data.file_path= audio_path
        new_data.file_with_user = 0 # 1 if user validating this instance
        new_data.instance_validated = 1 #1 if human validated this instance
        new_data.instance_valid = 1 # 1 if instance is ok
        new_data.user_validated = 'edresson'
        db.session.add(new_data)
    db.session.commit()

if __name__ == '__main__':
    from waitress import serve
    #serve(app, host="0.0.0.0", port=80) # for product server
    manager.run()
