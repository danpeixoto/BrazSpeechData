# coding: utf-8

import random
import string
from functools import wraps
import hashlib
from datetime import datetime
import datetime as dtt
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
from sqlalchemy import asc, desc
import math
from models import db
from models import User, Dataset, TimeValidated
import os


def hash_and_salt(password):
	password_hash = hashlib.sha256()
	salt = ''.join(random.choice(string.ascii_letters + string.digits)
				   for i in range(8))
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


webui = Blueprint('webui', __name__, static_folder='static',
				  static_url_path='/static/webui', template_folder='templates')


def check_current_user(data):
	if (data.number_validated == 0):
		data.user_validated = session['username']
	elif (data.number_validated == 1):
		data.user_validated2 = session['username']
	elif (data.number_validated == 2):
		data.user_validated3 = session['username']


def check_current_valids(data, valid_list):

	if (data.valids_user1 == ''):
		data.valids_user1 = valid_list
	elif (data.valids_user2 == ''):
		data.valids_user2 = valid_list
	else:
		data.valids_user3 = valid_list


def check_current_invalids(data, invalidClass):

	if (data.invalid_user1 == 0):
		data.invalid_user1 = invalidClass
	elif (data.invalid_user2 == 0):
		data.invalid_user2 = invalidClass
	else:
		data.invalid_user3 = invalidClass


def check_current_reason(data, invalid_reason):

	if (data.invalid_reason1 == ''):
		data.invalid_reason1 = invalid_reason
	elif (data.invalid_reason2 == ''):
		data.invalid_reason2 = invalid_reason
	else:
		data.invalid_reason3 = invalid_reason


# Parte de contagem de tempo

# Função que calcula e armazena o tempo gasto por cada usuário.
def Duration_calculation(last_time, present_time):
	time_difference = present_time - last_time
	time_difference_on_seconds = time_difference.seconds
	duration = min(time_difference_on_seconds, 120)
	return int(duration)

# Função que calcula o total de tempo gasto pelo usuário com base no intervalo de tempo exigido.


def Total_duration_user(date_1, date_2, current_user):
	all_duration = TimeValidated.query.filter_by(
		user_validated=current_user).all()
	total_hours = 0
	for total in all_duration:
		if (total.time_validated >= date_1 and total.time_validated <= date_2):
			total_hours += total.duration

	return total_hours/3600.0


# Função que calcula o total de tempo gasto pelo usuário com base no intervalo de tempo, no caso de todos os usuários.
def Total_duration_admin(date_1, date_2):
	all_users = User.query.all()
	users_data = ""
	for user in all_users:
		if(len(user.username) > 10 and " " not in user.username):
			#all_duration = TimeValidated.query.filter_by(user_validated=user.username).all()
			all_duration = TimeValidated.query.filter(
				TimeValidated.user_validated == user.username, TimeValidated.time_validated >= date_1, TimeValidated.time_validated <= date_2)

			total_hours = 0
			for total in all_duration:
				total_hours += total.duration

			users_data += u'{},{:.2f};'.format(user.username,
											   total_hours/3600.0)

	return users_data


def check_invalid_reason(invalid_reason):
	return invalid_reason if invalid_reason != None else 'None'


def check_valids(values_list):
	valid_list = [0, 0, 0, 0, 0]

	for i in range(5):
		valid_list[i-1] = i if 'Valid'+str(i) in values_list else 0

	return str(valid_list)


@webui.route('/', methods=['GET', 'POST'])
@require_login
def index():
	if request.method == 'POST':
		data = Dataset.query.filter_by(file_path=session['file_path']).first()
		last_time = TimeValidated.query.filter_by(
			user_validated=session['username']).order_by(desc(TimeValidated.id)).first()
		check_current_user(data)

		check_current_reason(data, check_invalid_reason(
			request.form.get('InvalidReason')))
		new_time = TimeValidated()
		data.instance_validated += 1
		data.file_with_user = 0
		data.number_validated += 1

		if request.form.getlist('Valid'):
			values_list = request.form.getlist('Valid')
			valid_list = check_valids(values_list)
			check_current_valids(data, valid_list)
			data.instance_valid = 1
		elif request.form.get('Invalid')[:-1] == 'Invalid':
			invalidClass = -int(request.form.get('Invalid')[-1])
			check_current_valids(data, 'None')
			check_current_invalids(data, invalidClass)

		new_time.user_validated = session['username']
		new_time.id_data = data.id
		new_time.time_validated = datetime.now()
		last_time_value = last_time.time_validated if last_time != None else datetime.now()
		new_time.duration = Duration_calculation(
			last_time_value, new_time.time_validated)
		db.session.add(data)
		db.session.add(new_time)
		db.session.commit()
		return redirect(url_for('webui.index'))

	if session['username'] == 'sandra' or session['username'] == 'edresson':
		data = Dataset.query.filter_by(
			instance_validated=0, file_with_user=0, data_gold=1).first()
	else:
		#data = session.query(Dataset).filter(Dataset.number_validated < 3, Dataset.file_with_user == 0, Dataset.data_gold == 0)
		data = Dataset.query.filter(Dataset.instance_validated < 3, Dataset.file_with_user < 1, Dataset.data_gold < 1, Dataset.user_validated !=
									session['username'], Dataset.user_validated2 != session['username'], Dataset.user_validated3 != session['username']).first()

	if data is None:
		return render_template('index-finish.html')
	else:

		data.file_with_user = 0
		session['text'] = data.text
		session['audio_lenght'] = data.audio_lenght
		session['file_path'] = data.file_path
		db.session.add(data)
		db.session.commit()
		
		data.file_path = os.path.join(
			'Dataset', data.file_path).replace('\\', '/')




		return render_template('index.html', dataset=data)



@webui.route('/tutorial', methods=['GET', 'POST'])
def tutorial():
	if request.method == 'POST':
		return redirect(url_for('webui.index'))
		# if request.form.get('sairtutorial') == 'Ir para Anotação':
	return render_template('tutorial.html')


@webui.route('/hours_worked', methods=['GET', 'POST'])
def hours_worked():

	response_string = ''

	first_week = Total_duration_user(datetime(2020, 10, 1, 0, 0, 0), datetime(
		2020, 10, 4, 23, 59, 59), session['username'])
	today = dtt.datetime.today()
	start = datetime(2020, 10, 5, 0, 0, 0)
	response_string += u'{},{},{:.2f};'.format(datetime(2020, 10, 1, 0, 0, 0).strftime(
		'%d-%m-%Y'), datetime(2020, 10, 4, 23, 59, 59).strftime('%d-%m-%Y'), first_week)
	num_weeks = abs(today-start).days//7 + 1

	total_listened_since_start = 0
	total_listened_since_start += first_week
	for i in range(num_weeks-1):

		monday = start + dtt.timedelta(days=i*7)
		sunday = monday + dtt.timedelta(days=6)
		next_monday = monday + dtt.timedelta(days=7)
		hours_listened = Total_duration_user(
			monday, next_monday, session['username'])
		#total_listened_since_start += hours_listened
		response_string += u'{},{},{:.2f};'.format(monday.strftime(
			'%d-%m-%Y'), sunday.strftime('%d-%m-%Y'), hours_listened)

	today = dtt.datetime.today()
	last_monday = today - dtt.timedelta(days=today.weekday(), hours=today.hour,
										minutes=today.minute, seconds=today.second, microseconds=today.microsecond)
	hours_listened = Total_duration_user(
		last_monday, today, session['username'])

	#total_listened_since_start += hours_listened

	response_string += u'{},{},{:.2f};'.format(last_monday.strftime('%d-%m-%Y'), today.strftime('%d-%m-%Y'), hours_listened)
	#response_string += u'{},{},{:.2f};'.format(datetime(2020, 10, 1, 0, 0, 0).strftime('%d-%m-%Y'), today.strftime('%d-%m-%Y'), total_listened_since_start)

	'''
	if request.method == 'POST':
		today= dtt.datetime.today()
		if request.form.get('segunda'):
			last_monday =  today - dtt.timedelta(days=today.weekday())
			next_monday = today + dtt.timedelta(days=-today.weekday(), weeks=1)
			hours_listened = Total_duration_user(last_monday,today,session['username'])
			total_hours = 20
			response_string = 'Você trabalhou {} essa semana. Semana atual: {} até {}'.format(hours_listened, str(last_monday)[:10],str(next_monday)[:10])
		elif request.form.get('comeco'):
			comeco = datetime(2020,10,1,0,0,0)
			total_hours =  today - comeco
			total_hours =  total_hours.days*24.0
			hours_listened = Total_duration_user(comeco,today,session['username'])
			response_string = 'Você trabalhou {} essa desde a data 01/10/2020. O total de horas desde o inicio do projeto foi de {} horas'.format(hours_listened,total_hours)
	'''
	#Aqui eu pesquiso a carga horaria do anotador, caso ele não seja anotador comum recebe 20
	user_data = User.query.filter(User.username == session['username'])
	for user in user_data:
		workload = user.carga_horaria if user.carga_horaria else 20
	
	return render_template('hours_worked.html', hours={'response_string': response_string, 'workload': workload})


@webui.route('/admin', methods=['GET', 'POST'])
@require_admin
def admin():
	instances = []
	if request.method == 'POST':
		if request.form.get('Download Valid instances'):
			if request.form.get('Download Valid instances')[-5:] == 'Valid':

				gold = 0 if 'Gold' not in request.form.get(
					'Download Valid instances') else 1
				# tive que colocar dessa maneira, pq tinhamos decidido que a sandra e o edresson validariam audios diferentes
				total_pessoas = 3-(gold*2)
				data = Dataset.query.filter(
					Dataset.number_validated >= total_pessoas, (Dataset.valids_user1 != 'None') or (Dataset.valids_user2 != 'None') or (Dataset.valids_user3 != 'None'), Dataset.data_gold == gold)
				csv = ''

				for dt in data:
					string = dt.file_path+';'+str(dt.audio_lenght)+';'+dt.text+';'+dt.valids_user1+';'+dt.valids_user2+';'+dt.valids_user3+';'+str(dt.invalid_user1)+';'+str(dt.invalid_user2)+';'+str(dt.invalid_user3) +\
						';'+dt.invalid_reason1+';'+dt.invalid_reason2+';'+dt.invalid_reason3+';' +\
						str(dt.data_gold)+';'+str(dt.number_validated)+'\n'
					csv += string
				return Response(csv, mimetype='text/csv', headers={'Content-disposition': 'attachment; filename=valid_instances_{}.csv'.format(gold)})

		elif request.form.get('Download Invalid instances')[-9:-2] == 'Invalid':

			classe_invalid = - \
				int(request.form.get('Download Invalid instances')[-1])
			gold = 0 if 'Gold' not in request.form.get(
				'Download Invalid instances') else 1
			# tive que colocar dessa maneira, pq tinhamos decidido que a sandra e o edresson validariam audios diferentes
			total_pessoas = 3-(gold*2)
			data = Dataset.query.filter(Dataset.number_validated >= total_pessoas, (Dataset.invalid_user1 == classe_invalid) | (
				Dataset.invalid_user2 == classe_invalid) | (Dataset.invalid_user3 == classe_invalid), Dataset.data_gold == gold)
			csv = ''
			for dt in data:
				string = dt.file_path+';'+str(dt.audio_lenght)+';'+dt.text+';'+dt.valids_user1+';'+dt.valids_user2+';'+dt.valids_user3+';'+str(dt.invalid_user1)+';'+str(dt.invalid_user2)+';'+str(dt.invalid_user3) +\
					';'+dt.invalid_reason1+';'+dt.invalid_reason2+';'+dt.invalid_reason3+';' +\
					str(dt.data_gold)+';'+str(dt.number_validated)+'\n'
				csv += string
			return Response(csv, mimetype='text/csv', headers={'Content-disposition': 'attachment; filename=invalid_instances_{}.csv'.format(-classe_invalid)})

	today = dtt.datetime.today()
	return render_template('admin.html', hours={'user_list': Total_duration_admin(datetime(2020, 10, 1, 0, 0, 0), today), "today": today.strftime('%d-%m-%Y'), "start": datetime(2020, 10, 1, 0, 0, 0).strftime('%d-%m-%Y')})


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
				user = User.query.filter_by(
					username=request.form['username']).first()
				password_hash = hashlib.sha256()
				password_hash.update(
					(user.salt + request.form['password']).encode())
			except:
				flash('User is not identified, try again!')
				return redirect(url_for('webui.login'))
			if user is not None:
				if user.password == password_hash.hexdigest():
					session['username'] = request.form['username']
					last_login_time = user.last_login_time
					last_login_ip = user.last_login_ip
					user.last_login_time = datetime.now()
					user.last_login_ip = request.remote_addr
					db.session.commit()
					flash('Logged in successfully.')
					if last_login_ip:
						flash('Last login from ' + last_login_ip + ' on ' +
							  last_login_time.strftime('%d/%m/%y %H:%M'))
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
			admin_user = User.query.filter_by(
				username=session['username']).first()
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
			flash('User '+request.form['username'] +
				  ' successfully registered')
			return redirect(url_for('webui.admin'))
	return render_template('create_user.html')


@webui.route('/logout')
def logout():
	session.pop('username', None)
	flash('Logged out successfully.')
	return redirect(url_for('webui.login'))


# ESSA FUNÇÂO É PARA ARRUMAR A COLUNA DURATION DO TIMEVALIDATED
def funcao_soma_valores_anotadore():
	all_users = User.query.all()

	for user in all_users:
		all_times = TimeValidated.query.filter_by(user_validated=user.username)
		i = 0
		last_time = 0
		for time in all_times:
			if(i == 0):
				time.duration = 120
				i += 1
				last_time = time.time_validated
			else:
				time.duration = Duration_calculation(
					last_time, time.time_validated)
				last_time = time.time_validated

			db.session.commit()
