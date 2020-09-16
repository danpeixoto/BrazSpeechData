import random
import string
from functools import wraps
import hashlib
from datetime import datetime

from flask import Blueprint
from flask import abort
from flask import request
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import flash
from flask import send_from_directory
from flask import current_app, Response

from models import db
from models import User, Dataset, TimeValidated
import os

def hash_and_salt(password):
	password_hash = hashlib.sha256()
	salt = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
	password_hash.update((salt + request.form['password']).encode())
	return password_hash.hexdigest(), salt


def require_admin(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if 'username' in session and session['username'] == 'admin':
			return func(*args, **kwargs)
		else:
			return redirect(url_for('webui.login'))
	return wrapper


def require_login(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if 'username' in session:
			return func(*args, **kwargs)
		else:
			return redirect(url_for('webui.login'))
	return wrapper



webui = Blueprint('webui', __name__, static_folder='static', static_url_path='/static/webui', template_folder='templates')


@webui.route('/', methods=['GET','POST'])
@require_login
def index():
	if request.method == 'POST':

		if request.form.get('Valid') == 'Valid':
			new_time = TimeValidated()
			data = Dataset.query.filter_by(file_path =  session['file_path']).first()
			data.instance_validated= 1
			data.file_with_user = 0
			data.instance_valid= 1
			data.number_validated += 1
			new_time.user_validated = session['username']
			new_time.id_data = data.id
			new_time.time_validated = datetime.now()
			data.user_validated = session['username']
			db.session.add(data)
			db.session.add(new_time)
			db.session.commit()
		elif request.form.get('Invalid')[:-1] == 'Invalid':
			invalidClass = -int(request.form.get('Invalid')[-1])
			data = Dataset.query.filter_by(file_path =  session['file_path']).first()
			new_time = TimeValidated()
			data.instance_validated= 1
			data.file_with_user = 0
			data.number_validated += 1
			data.instance_valid= invalidClass
			new_time.user_validated = session['username']
			new_time.id_data = data.id
			new_time.time_validated = datetime.now()
			data.user_validated = session['username']
			db.session.add(data)
			db.session.add(new_time)
			db.session.commit()
		
		return redirect(url_for('webui.index'))

	if session['username'] == 'sandra' or session['username'] == 'edresson':
		data = Dataset.query.filter_by(instance_validated=0,file_with_user=0, data_gold = 1).first()
	else:
		data = Dataset.query.filter_by(instance_validated=0,file_with_user=0, data_gold = 0).first()
		
	if data is None:
		return render_template('index-finish.html')
	else:
		data.file_with_user = 1
		session['text'] = data.text
		session['audio_lenght'] = data.audio_lenght
		session['file_path']= data.file_path
		db.session.add(data)
		db.session.commit()
		
		data.file_path=os.path.join('Dataset',data.file_path).replace("\\","/")

		return render_template('index.html',dataset=data)


@webui.route('/tutorial', methods=['GET', 'POST'])
def tutorial():
	if request.method == 'POST':
		return redirect(url_for('webui.index'))
		#if request.form.get('sairtutorial') == 'Ir para Anotação':
	return render_template('tutorial.html')
	

@webui.route('/admin', methods=['GET', 'POST'])
@require_admin
def admin():
	instances = []
	if request.method == 'POST':
		if request.form.get('Download Valid instances') == 'Download Valid instances':
			data = Dataset.query.filter_by(instance_valid=1)
			csv = ""
			for dt in data: 
				string = dt.file_path+','+str(dt.audio_lenght)+','+dt.text+'\n'
				csv+=string
			return Response(csv,mimetype="text/csv", headers={"Content-disposition":"attachment; filename=valid_instances.csv"})
		elif request.form.get("Download Invalid instances 1") == "Download Invalid instances 1":
			data = Dataset.query.filter_by(instance_valid=-1,instance_validated=1)
			csv = ""
			for dt in data: 
				string = dt.file_path+','+str(dt.audio_lenght)+','+dt.text+'\n'
				csv+=string
			return Response(csv,mimetype="text/csv", headers={"Content-disposition":"attachment; filename=invalid_instances_1.csv"})
		elif request.form.get("Download Invalid instances 2") == "Download Invalid instances 2":
			data = Dataset.query.filter_by(instance_valid=-2,instance_validated=1)
			csv = ""
			for dt in data: 
				string = dt.file_path+','+str(dt.audio_lenght)+','+dt.text+'\n'
				csv+=string
			return Response(csv,mimetype="text/csv", headers={"Content-disposition":"attachment; filename=invalid_instances_2.csv"})
		elif request.form.get("Download Invalid instances 3") == "Download Invalid instances 3":
			data = Dataset.query.filter_by(instance_valid=-3,instance_validated=1)
			csv = ""
			for dt in data: 
				string = dt.file_path+','+str(dt.audio_lenght)+','+dt.text+'\n'
				csv+=string
			return Response(csv,mimetype="text/csv", headers={"Content-disposition":"attachment; filename=invalid_instances_3.csv"})
		elif request.form.get("Download Invalid instances 4") == "Download Invalid instances 4":
			data = Dataset.query.filter_by(instance_valid=-4,instance_validated=1)
			csv = ""
			for dt in data: 
				string = dt.file_path+','+str(dt.audio_lenght)+','+dt.text+'\n'
				csv+=string
			return Response(csv,mimetype="text/csv", headers={"Content-disposition":"attachment; filename=invalid_instances_4.csv"})
		elif request.form.get("Download Invalid instances 5") == "Download Invalid instances 5":
			data = Dataset.query.filter_by(instance_valid=-5,instance_validated=1)
			csv = ""
			for dt in data: 
				string = dt.file_path+','+str(dt.audio_lenght)+','+dt.text+'\n'
				csv+=string
			return Response(csv,mimetype="text/csv", headers={"Content-disposition":"attachment; filename=invalid_instances_5.csv"})
		elif request.form.get("Download Invalid instances 6") == "Download Invalid instances 6":
			data = Dataset.query.filter_by(instance_valid=-6,instance_validated=1)
			csv = ""
			for dt in data: 
				string = dt.file_path+','+str(dt.audio_lenght)+','+dt.text+'\n'
				csv+=string
			return Response(csv,mimetype="text/csv", headers={"Content-disposition":"attachment; filename=invalid_instances_6.csv"})	
		elif request.form.get("Download Invalid instances 7") == "Download Invalid instances 7":
			data = Dataset.query.filter_by(instance_valid=-7,instance_validated=1)
			csv = ""
			for dt in data: 
				string = dt.file_path+','+str(dt.audio_lenght)+','+dt.text+'\n'
				csv+=string
			return Response(csv,mimetype="text/csv", headers={"Content-disposition":"attachment; filename=invalid_instances_7.csv"})	
	return render_template('admin.html')


@webui.route('/login', methods=['GET', 'POST'])
def login():
	admin_user = User.query.filter_by(username='admin').first()
	if not admin_user:
		if request.method == 'POST':
			if 'password' in request.form:
				password_hash, salt = hash_and_salt(request.form['password']) 
				new_user = User()
				new_user.username = 'admin'
				new_user.password = password_hash
				new_user.salt = salt
				db.session.add(new_user)
				db.session.commit()
				flash('Password set successfully. Please log in.')
				return redirect(url_for('webui.login'))
		return render_template('create_password.html')
	if request.method == 'POST':
		if request.form['password'] and request.form['username']:
				try:
					user = User.query.filter_by(username=request.form['username']).first()
					password_hash = hashlib.sha256()
					password_hash.update((user.salt + request.form['password']).encode())
				except:
					flash('User is not identified, try again!')
					return redirect(url_for('webui.login'))
				if user is not None:
					if user.password == password_hash.hexdigest():
						session['username'] = request.form['username']
						last_login_time =  user.last_login_time
						last_login_ip = user.last_login_ip
						user.last_login_time = datetime.now()
						user.last_login_ip = request.remote_addr 
						db.session.commit()
						flash('Logged in successfully.') 
						if last_login_ip:
							flash('Last login from ' + last_login_ip + ' on ' + last_login_time.strftime("%d/%m/%y %H:%M"))
						if session['username'] == 'admin':
							return redirect(url_for('webui.admin'))
						else:
							return redirect(url_for('webui.index'))
					else:
						flash('Wrong password')
				else:
					flash('This user is not registered. Contact an administrator !')
	return render_template('login.html')


@webui.route('/passchange', methods=['GET', 'POST'])
@require_login
def change_password():
	if request.method == 'POST':
		if 'password' in request.form:
			admin_user = User.query.filter_by(username=session['username']).first()
			password_hash, salt = hash_and_salt(request.form['password'])
			admin_user.password = password_hash
			admin_user.salt = salt
			db.session.add(admin_user)
			db.session.commit()
			flash('Password reset successfully. Please log in.')
			return redirect(url_for('webui.login'))
	return render_template('create_password.html')

@webui.route('/adduser', methods=['GET', 'POST'])
@require_admin
def add_user():
	if request.method == 'POST':
		if 'password' in request.form and 'username' in request.form:
			print(request.form['password'])
			password_hash, salt = hash_and_salt(request.form['password']) 
			new_user = User()
			new_user.username = request.form['username']
			new_user.password = password_hash
			new_user.salt = salt
			db.session.add(new_user)
			db.session.commit()
			flash('User '+request.form['username']+ ' successfully registered')
			return redirect(url_for('webui.admin'))
	return render_template('create_user.html')


@webui.route('/logout')
def logout():
	session.pop('username', None)
	flash('Logged out successfully.')
	return redirect(url_for('webui.login'))

