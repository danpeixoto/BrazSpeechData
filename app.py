# coding: utf-8
import random
import string
import hashlib
from functools import wraps
import datetime
import os
import shutil
import tempfile

from flask import Flask
from flask import session
from flask_script import Manager
from flask import Blueprint
from flask import abort
from flask import request
from flask import redirect
from flask import render_template
from flask import url_for
from flask import flash
from flask import send_from_directory
from flask import current_app, Response

from models import db, Dataset, User, TimeValidated
from webui import webui
from config import config 

import pymysql
pymysql.install_as_MySQLdb()

# csv data from make dataset
data_csv = 'static/Dataset/metadata.csv'
data_csv_transcribe = 'static/Dataset/metadata_transcribe.csv'
data_validated_csv = 'static/Dataset/metadata_validated.csv'
data_csv_gold = 'static/Gold/metadata_gold.csv' 
data_ted = 'static/Dataset/metadata_ted.csv'

app = Flask(__name__)
app.config.from_object(config['dev'])
app.register_blueprint(webui)
#app.register_blueprint(api, url_prefix='/api')
db.init_app(app)
manager = Manager(app)


@app.after_request
def headers(response):
	response.headers['Server'] = 'Audio-Validation'
	return response


@manager.command
def initdb():
	db.drop_all()
	db.create_all()
	db.session.commit()


@manager.command
def initdataset():

	lines = list(open(data_ted,encoding='utf8').readlines())   
	
	for line in lines:
		audio_path,lenght,text, text_asr = line.split(',')
		duration = text.replace('\n','')
		text_asr = text_asr.replace('\n','')
		new_data= Dataset()
		new_data.text_asr = text_asr
		new_data.text = ''
		new_data.audio_lenght = lenght
		new_data.file_path= audio_path
		new_data.instance_validated = 0 #1 if human validated this instance
		new_data.file_with_user = 0 # 1 if user validating this instance
		new_data.invalid_user1 = 0
		new_data.invalid_user2 = 0
		new_data.invalid_user3= 0
		new_data.valids_user1 = ''
		new_data.valids_user2 = ''
		new_data.valids_user3 = ''
		new_data.user_validated = ''
		new_data.user_validated2 = ''
		new_data.user_validated3 = ''
		new_data.invalid_reason1 = ''
		new_data.invalid_reason2 = ''
		new_data.invalid_reason3 = ''
		new_data.number_validated = 0 
		new_data.data_gold = 0
		new_data.duration = duration
		new_data.task = 1
		new_data.travado = None
		db.session.add(new_data)
	db.session.commit()

@manager.command
def initvalidateddataset():
	lines = list(open(data_validated_csv).readlines())

	for line in lines:
		audio_path, duration, travado, lenght, text, task, text_asr, invalid_reason, number_validated, type_validated_1, type_validated_2, type_validated_3, type_validated_4, type_validated_5, type_validated_6, data_gold = line.split(',')
		text = text.replace('\n','')
		new_data= Dataset()
		new_data.text = text
		new_data.invalid_reason = invalid_reason
		new_data.audio_lenght = lenght
		new_data.file_path= audio_path
		new_data.file_with_user = 0 # 1 if user validating this instance
		new_data.instance_validated = 1 #1 if human validated this instance
		new_data.instance_valid = 1 # 1 if instance is ok
		new_data.number_validated = number_validated 
		new_data.data_gold = data_gold
		new_data.user_validated = ''
		new_data.user_validated2 = ''
		new_data.user_validated3 = ''
		new_data.type_validated_1 = type_validated_1
		new_data.type_validated_2 = type_validated_2
		new_data.type_validated_3 = type_validated_3
		new_data.type_validated_4 = type_validated_4
		new_data.type_validated_5 = type_validated_5
		new_data.type_validated_6 = type_validated_6
		new_data.duration = duration
		new_data.travado = travado
		new_data.task = task
		new_data.text_asr = text_asr
		db.session.add(new_data)
	db.session.commit()

if __name__ == '__main__':
	from waitress import serve
	#serve(app, host='0.0.0.0', port=80) # for product server
	manager.run()
