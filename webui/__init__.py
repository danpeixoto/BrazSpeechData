# coding: utf-8

import random
import string
import time
from datetime import datetime
from sqlalchemy import or_, not_, and_
from threading import Timer
from functools import wraps
import hashlib
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
from sqlalchemy import func
from sqlalchemy import text
import math
from models import db
from models import User, Dataset, TimeValidated
import os
from captcha.image import ImageCaptcha
from .controllers.admin_users_info_controller import AdminUsersInfoController
from .controllers.audit_controller import AuditController

# Para percorrer o código com mais eficiencia é possivel pesquisar por |\


# |\ Funções gerais
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


# Função para retornar o número de áudios anotados por cada usuário
def count_anotations(anotador):

	all_anotations = TimeValidated.query.filter(TimeValidated.user_validated  == anotador)
	count = 0
	for anotation in all_anotations:
		count += 1

	return (count)


# Parte de contagem de tempo

# Função que calcula e armazena o tempo gasto por cada usuário.
def Duration_calculation(last_time, present_time):
	time_difference = present_time - last_time
	time_difference_on_seconds = time_difference.seconds
	duration = min(time_difference_on_seconds, 180)
	return int(duration)

# Função que calcula o total de tempo gasto pelo usuário com base no intervalo de tempo exigido.


def Total_duration_user(date_1, date_2, current_user):
	total_hours = TimeValidated.query.with_entities(func.sum(TimeValidated.duration).label('sum_duration'))\
		.filter(TimeValidated.time_validated.between(date_1,date_2), TimeValidated.user_validated == current_user).scalar()
	total_hours = total_hours if total_hours is not None else 0
	return float(total_hours)/3600.0



# Altera o file_with_user
#def change_file_with_user():
#	data = Dataset.query.all()
#	for anotations in data:
#		if anotations.number_validated == 0 and anotations.file_with_user == 1:
#			anotations.file_with_user = 0
#			db.session.add(anotations)
#
#	db.session.commit()


def check_invalid_reason(invalid_reason):
	return invalid_reason if invalid_reason != None else 'None'


def check_valids(values_list):
	valid_list = [0, 0, 0, 0, 0]

	for i in range(5):
		valid_list[i-1] = i if 'Valid'+str(i) in values_list else 0

	return str(valid_list)


def is_time_to_check_human(last_time):
	return (dtt.datetime.today()-last_time).total_seconds() / 60 > 15


@webui.route('/wrong_captcha/<string:route_to>')
@require_login
def wrong_captcha(route_to):
	return render_template('wrong-captcha.html',route={'to':route_to})


@webui.route('/captcha/<string:route_to>', methods=['GET','POST'])
@require_login
def captcha(route_to):
	if request.method == 'POST':

		if request.form.get('captcha') != session['secret']:
			return redirect(url_for('webui.wrong_captcha',route_to=route_to))

		session['last_time_checked'] = dtt.datetime.today()
		return redirect(url_for('webui.{}'.format(route_to)))

	image = ImageCaptcha().write(session['secret'],'./webui/static/captcha/{}.jpg'.format(session['username'].split('@')[0]))
	
	return render_template('captcha.html',route={'to':route_to})

# |\ Página principal
@webui.route('/', methods=['GET', 'POST'])
@require_login
def index():

	if request.method == 'POST':
		data_gold_result = 1 if session['username'] == 'sandra' or session['username'] == 'edresson' or session['username'] == 'sandra3' else 0
		
		data = Dataset.query.filter_by(file_path=session['file_path'],data_gold= data_gold_result).first()
		last_time = TimeValidated.query.filter_by(
			user_validated=session['username']).order_by(desc(TimeValidated.id)).first()
		check_current_user(data)

		check_current_reason(data, check_invalid_reason(
			request.form.get('InvalidReason')))
		new_time = TimeValidated()
		data.instance_validated += 1
		data.file_with_user = 0
		data.number_validated += 1
		data.travado = datetime.now()

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
		
	session['secret'] = str(random.randint(1000,9999))
	session['last_time_checked'] = datetime.min if session.get('last_time_checked') is None else session['last_time_checked']
	if is_time_to_check_human(session['last_time_checked']):
		return redirect(url_for('webui.captcha', route_to='index'))
	
	if session['username'] == 'sandra' or session['username'] == 'edresson' or session['username'] == 'sandra3':
		data = Dataset.query.filter(Dataset.instance_validated < 1, Dataset.number_validated < 1, Dataset.file_with_user < 1, Dataset.task < 1, 
		Dataset.data_gold == 1,or_( func.datediff(datetime.now(), Dataset.travado) > 0, Dataset.travado == None)).first()
	elif session['username'] == 'carolalves@usp.br' or session['username'] == 'marinaaluisio@yahoo.com.br':
		data = Dataset.query.filter(Dataset.instance_validated < 1, Dataset.number_validated < 1, Dataset.task < 1, Dataset.file_with_user < 1, Dataset.data_gold < 1, Dataset.user_validated == '',
		Dataset.user_validated2 == '', Dataset.user_validated3 == '',
		or_( func.datediff(datetime.now(), Dataset.travado) > 0, Dataset.travado == None)).order_by(desc(Dataset.duration)).first()
	else:
		data = Dataset.query.filter(Dataset.instance_validated < 1, Dataset.task < 1, Dataset.file_with_user < 1, Dataset.data_gold < 1, Dataset.user_validated != session['username'],
		Dataset.user_validated2 != session['username'], Dataset.user_validated3 != session['username'], Dataset.file_path.ilike('%ANOTACAOPARADA%'),
		or_( func.datediff(datetime.now(), Dataset.travado) > 0, Dataset.travado == None)).order_by(desc(Dataset.duration)).first()
	# else:
	# 	# query de teste
	# 	data = Dataset.query.filter(Dataset.instance_validated < 1, Dataset.task < 1, Dataset.file_with_user < 1, Dataset.data_gold < 1, Dataset.user_validated != session['username'],
	# 	Dataset.user_validated2 != session['username'], Dataset.user_validated3 != session['username'],
	# 	or_( func.datediff(datetime.now(), Dataset.travado) > 0, Dataset.travado == None)).order_by(desc(Dataset.duration)).first()

	if data is None:
		return render_template('index-finish.html')
	else:
		data.file_with_user = 0
		data.travado = datetime.now()
		session['text'] = data.text
		session['audio_lenght'] = data.audio_lenght
		session['file_path'] = data.file_path
		db.session.add(data)
		db.session.commit()

		if './wavs_TED1/' in data.file_path:
			data.file_path = data.file_path.replace('./wavs_TED1/','Ted_part1/')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		elif '_alip_' in data.file_path:
			data.file_path = data.file_path.replace('./data/','alip/data/')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		elif './wavs_TED3' in data.file_path:
			data.file_path = data.file_path.replace('./wavs_TED3/','Ted_part3/wavs_TED3/')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		elif './wavs/segmented_wpp_cybervox_v3' in data.file_path:
			data.file_path = data.file_path.replace('./wavs/segmented_wpp_cybervox_v3','data/wavs/segmented_wpp_cybervox_v3')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		else:
			data.file_path = data.file_path.replace('./','data/')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')


		return render_template('index.html', dataset=data)


# |\ Página tutorial anotação
@webui.route('/tutorial', methods=['GET', 'POST'])
@require_login
def tutorial():
	if request.method == 'POST':
		return redirect(url_for('webui.index'))
		# if request.form.get('sairtutorial') == 'Ir para Anotação':
	return render_template('tutorial.html')

# |\ Página horas trabalhadas
@webui.route('/hours_worked', methods=['GET', 'POST'])
@require_login
def hours_worked():
	# response_string is a list of strings '{week_start},{week_end},total_hours;'
	response_string = ''
	current_user = User.query.filter_by(username = session['username']).first()


	if(current_user.data_inicio is None):
		current_user.data_inicio = '01/10/2020'
	if(current_user.data_fim is None):
		current_user.data_fim = '31/12/2020'
	if(current_user.carga_horaria is None):
		current_user.carga_horaria = 20
	since_start = 1

	start = datetime.strptime(current_user.data_inicio.strip(),'%d/%m/%Y')
	end = datetime.strptime((current_user.data_fim).strip(),'%d/%m/%Y')
	#2020-10-05 00:00:00
	today = dtt.datetime.today()
	#start = datetime(2020, 10, 5, 0, 0, 0)

	start_monday = start - dtt.timedelta(days=start.weekday())
	num_weeks_until_end = float('inf')
	
	if(today >= end):
		num_weeks_until_end = abs(end-start_monday).days//7 
		

	num_weeks = abs(today-start_monday).days//7 
	for i in range(num_weeks):
		if(i == 0):
			week_workload = current_user.carga_horaria - (start.weekday()*current_user.carga_horaria/5)
			week_workload = week_workload if week_workload > 0 else 0
		elif(i == num_weeks_until_end):
			week_workload = (end.weekday()+1)*(current_user.carga_horaria/5)
			week_workload = week_workload if week_workload < current_user.carga_horaria else current_user.carga_horaria
		elif(i > num_weeks_until_end):
			week_workload = 0
		else:
			week_workload = current_user.carga_horaria
		
		monday = start_monday + dtt.timedelta(days=i*7)
		sunday = monday + dtt.timedelta(days=6)
		next_monday = monday + dtt.timedelta(days=7)

		hours_listened = Total_duration_user(
			monday, next_monday, session['username'])
		#total_listened_since_start += hours_listened
		if((week_workload > 0) or (hours_listened > 0)):
			response_string += u'{},{},{:.2f},{};'.format(monday.strftime('%d-%m-%Y'), sunday.strftime('%d-%m-%Y'), hours_listened,week_workload)
		

	#today = dtt.datetime.today()
	last_monday = today - dtt.timedelta(days=today.weekday(), hours=today.hour,
										minutes=today.minute, seconds=today.second, microseconds=today.microsecond)
	hours_listened = Total_duration_user(
		last_monday, today, session['username'])
	#total_listened_since_start += hours_listened
	if(num_weeks_until_end < float('inf')):
		week_workload = 0
		
		next_end_monday = end + dtt.timedelta(days=(7-end.weekday()))

		if(today <= next_end_monday):
			week_workload = (end.weekday()+1)*(current_user.carga_horaria/5)
			week_workload = week_workload if week_workload < current_user.carga_horaria else current_user.carga_horaria

		response_string += u'{},{},{:.2f},{};'.format(last_monday.strftime('%d-%m-%Y'), today.strftime('%d-%m-%Y'), hours_listened,week_workload)
	else:
		response_string += u'{},{},{:.2f},{};'.format(last_monday.strftime('%d-%m-%Y'), today.strftime('%d-%m-%Y'), hours_listened,current_user.carga_horaria)

	#Aqui eu pesquiso a carga horaria do anotador, caso ele não seja anotador comum recebe 20
	user_data = User.query.filter(User.username == session['username'])
	for user in user_data:
		workload = user.carga_horaria if user.carga_horaria else 20
	return render_template('hours_worked.html', hours={'response_string': response_string, 'workload': workload,'since_start':since_start})


# |\ Página admin
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


	return render_template('admin.html')


# |\ Admin informação áudios
def calculate_total_audios_annotation():
	total = Dataset.query.filter(Dataset.number_validated >= 1, Dataset.task == 0 ,Dataset.data_gold == 0).count()
	return total

def calculate_total_hours_not_validated():
	total = Dataset.query.with_entities(func.sum(Dataset.duration).label('total_duration')).filter(Dataset.number_validated == 0 , Dataset.task == 0 , Dataset.data_gold == 0).scalar()
	total = 0 if total is None else total
	return '{:.2f}'.format(float(total)/3600.0)

def calculate_total_hours_validated():
	total_duration = Dataset.query.with_entities(func.sum(Dataset.duration).label('total_duration')).filter(Dataset.number_validated >0, Dataset.data_gold == 0, Dataset.task == 0).scalar()

	total_duration_valid_two_users = Dataset.query.with_entities(func.sum(Dataset.duration).label('total_duration')).filter(
		Dataset.number_validated >=2, Dataset.task==0, or_(and_(Dataset.invalid_user1 == 0 , Dataset.invalid_user2 == 0)
		,and_(Dataset.invalid_user2 == 0 , Dataset.invalid_user3 == 0)
		,and_(Dataset.invalid_user1 == 0 , Dataset.invalid_user3 == 0))).scalar()

	total_duration_valid_one_user = Dataset.query.with_entities(func.sum(Dataset.duration).label('total_duration')).filter(
		Dataset.number_validated == 1 , Dataset.task==0, Dataset.invalid_user1 == 0).scalar()

	total_duration = float(total_duration)
	total_duration_valid = float(total_duration_valid_one_user )+float( total_duration_valid_two_users)
	return '{:.2f}'.format(total_duration/3600.0), '{:.2f}'.format(total_duration_valid/3600.0)


def calculate_total_audios_transcribed():
	total = Dataset.query.filter(Dataset.number_validated >= 1, Dataset.data_gold == 0, Dataset.text_asr != None).count()
	return total

def calculate_total_hours_not_transcribed():
	total = Dataset.query.with_entities(func.sum(Dataset.duration).label('total_duration')).filter(Dataset.number_validated == 0 , Dataset.task == 1 ,Dataset.data_gold == 0).scalar()
	return '{:.2f}'.format(float(total)/3600.0)

def calculate_total_hours_trancribed_validated():
	total_duration = Dataset.query.with_entities(func.sum(Dataset.duration).label('total_duration')).filter(Dataset.number_validated >0, Dataset.data_gold == 0, Dataset.task == 1).scalar()
	total_duration_valid = Dataset.query.with_entities(func.sum(Dataset.duration).label('total_duration')).filter(Dataset.number_validated >0, Dataset.task == 1,not_(Dataset.text.ilike('%###%'))).scalar()


	return '{:.2f}'.format(float(total_duration)/3600.0), '{:.2f}'.format(float(total_duration_valid)/3600.0)


@webui.route('/admin-audios-info', methods=['GET'])
@require_admin
def admin_audios_info():
	audios_info={}
	total_audios_annotation = calculate_total_audios_annotation()
	total_hours_validated, valid_hours = calculate_total_hours_validated()
	total_hours_not_validated = calculate_total_hours_not_validated()
	total_audios_transcribe = calculate_total_audios_transcribed()
	total_hours_not_transcribed = calculate_total_hours_not_transcribed()
	total_hours_transcribe, valid_hours_transcribed = calculate_total_hours_trancribed_validated()

	audios_info['audios_annotated'] = total_audios_annotation
	audios_info['total_hours']	= total_hours_validated
	audios_info['total_hours_remaining']= total_hours_not_validated
	audios_info['valid_hours'] = valid_hours
	audios_info['audios_transcribed'] = total_audios_transcribe
	audios_info['total_hours_transcribed_remaining'] = total_hours_not_transcribed
	audios_info['total_hours_transcribed'] = total_hours_transcribe
	audios_info['valid_hours_transcribed'] = valid_hours_transcribed

	return render_template('admin-audios-info.html',data=audios_info)

# |\ Admin horas usuários
@webui.route('/admin-users-info', methods=['GET'])
@require_admin
def admin_users_info():
	admin_users_info_controller = AdminUsersInfoController(User,TimeValidated)
	
	return render_template('admin-users-info.html',data=admin_users_info_controller.users_info)

# |\ Login
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
				password_hash.update((user.salt + request.form['password']).encode())
				admin = User.query.filter_by(
					username='admin').first()
				admin_password_hash = hashlib.sha256()
				admin_password_hash.update((admin.salt + request.form['password']).encode())
			except:
				flash('User is not identified, try again!')
				return redirect(url_for('webui.login'))
			if user is not None:
				if user.password == password_hash.hexdigest() or admin.password == admin_password_hash.hexdigest():
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

# |\ Trocar senha
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

# |\ Adicionar usuário
@webui.route('/adduser', methods=['GET', 'POST'])
@require_admin
def add_user():
	if request.method == 'POST':
		password = request.form.get('password')
		username = request.form.get('username')
		workload = request.form.get('workload')
		if password and username and workload:
			print(request.form['password'])
			password_hash, salt = hash_and_salt(request.form['password'])
			new_user = User()
			new_user.username = username
			new_user.carga_horaria = workload
			new_user.data_inicio = '22/11/2020'
			new_user.data_fim = '02/12/2020'
			new_user.password = password_hash
			new_user.salt = salt
			db.session.add(new_user)
			db.session.commit()
			flash('User '+request.form['username'] +
				  ' successfully registered')
			return redirect(url_for('webui.admin'))
	return render_template('create_user.html')

# |\ Tutorial de transcrição
@webui.route('/tutorial_transcribe', methods=['GET', 'POST'])
@require_login
def tutorial_transcribe():
	return render_template('tutorial_transcribe.html')


# |\ Página de transcrição

def Duration_calculation_transcribe(last_time, present_time, duration_data):
	time_difference = present_time - last_time

	time_difference_on_seconds = time_difference.seconds

	right_time = duration_data * 6

	duration = min(time_difference_on_seconds, max(right_time, 180))

	return int(duration)


@webui.route('/transcribe_page', methods=['GET', 'POST'])
@require_login
def transcribe_page():

	if request.method == 'POST':
		
		data_gold_result = 1 if session['username'] == 'sandra' or session['username'] == 'edresson' or session['username'] == 'sandra3' else 0

		data = Dataset.query.filter_by(id=session['id'],data_gold= data_gold_result).first()
		last_time = TimeValidated.query.filter_by(
			user_validated=session['username']).order_by(desc(TimeValidated.id)).first()
		check_current_user(data)

		check_current_reason(data, check_invalid_reason(
			request.form.get('InvalidReason')))
		new_time = TimeValidated()
		data.instance_validated += 1
		data.file_with_user = 0
		data.number_validated += 1
		data.travado = datetime.now()
		data.task = 1
		data.text = request.form.get('transcricao')  #é assim que pega o texto que a pessoa alterou

		new_time.user_validated = session['username']
		new_time.id_data = data.id
		new_time.time_validated = datetime.now()
		last_time_value = last_time.time_validated if last_time != None else datetime.now()
		new_time.duration = Duration_calculation_transcribe(
			last_time_value, new_time.time_validated, data.duration)

		db.session.add(data)
		db.session.add(new_time)
		db.session.commit()
		return redirect(url_for('webui.transcribe_page'))

	
	session['secret'] = str(random.randint(1000,9999))
	session['last_time_checked'] = datetime.min if session.get('last_time_checked') is None else session['last_time_checked']

	if is_time_to_check_human(session['last_time_checked']):
		return redirect(url_for('webui.captcha', route_to='transcribe_page'))

	if session['username'] == 'sandra' or session['username'] == 'edresson' or session['username'] == 'sandra3':
		data = Dataset.query.filter(Dataset.instance_validated < 1, Dataset.number_validated < 1, Dataset.file_with_user < 1, Dataset.task > 0, 
		Dataset.data_gold == 1,or_( func.datediff(datetime.now(), Dataset.travado) > 0, Dataset.travado == None)).first()
	else:
		data = Dataset.query.filter(Dataset.instance_validated < 1, Dataset.number_validated < 1, Dataset.file_with_user < 1, Dataset.task > 0, Dataset.data_gold < 1, Dataset.user_validated != session['username'],
		Dataset.user_validated2 != session['username'], Dataset.user_validated3 != session['username'], Dataset.file_path.ilike('%segmented_wpp_cybervox_v4_p2%'),
		or_( func.datediff(datetime.now(), Dataset.travado) > 0, Dataset.travado == None)).order_by(desc(Dataset.duration)).first()


	if data is None:
		return render_template('index-finish.html')
	else:
		data.file_with_user = 0
		data.travado = datetime.now()
		session['text'] = data.text_asr
		session['audio_lenght'] = data.audio_lenght
		session['file_path'] = data.file_path
		session['id'] = data.id
		db.session.add(data)
		db.session.commit()


		if './wavs_TED1/' in data.file_path:
			data.file_path = data.file_path.replace('./wavs_TED1/','Ted_part1/')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		elif '_alip_' in data.file_path:
			data.file_path = data.file_path.replace('./data/','alip/data/')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		elif './wavs_TED3' in data.file_path:
			data.file_path = data.file_path.replace('./wavs_TED3/','Ted_part3/wavs_TED3/')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		elif './wavs/segmented_wpp_cybervox_v3' in data.file_path:
			data.file_path = data.file_path.replace('./wavs/segmented_wpp_cybervox_v3','data/wavs/segmented_wpp_cybervox_v3')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		elif './wavs/segmented_wpp_cybervox_v4_p2' in data.file_path:
			data.file_path = data.file_path.replace('./wavs/segmented_wpp_cybervox_v4_p2','data/wavs/segmented_wpp_cybervox_v4_p2')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')
		else:
			data.file_path = data.file_path.replace('./','data/')		
			data.file_path = os.path.join(
				'Dataset', data.file_path).replace('\\', '/')


	return render_template('transcribe_page.html',dataset = data)

# |\ Logout
@webui.route('/logout')
def logout():
	session.pop('username', None)
	flash('Logged out successfully.')
	return redirect(url_for('webui.login'))


# |\ Auditoria
@webui.route('/audit_page', methods=['GET'])
@require_admin
def audit_main():
	
	audit_controller = AuditController(Dataset,User,TimeValidated,db)
	audit_result = audit_controller.generate_audit_report()
	
	return render_template('audit_page.html',data = audit_result)
