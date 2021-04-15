import datetime as dtt
from datetime import datetime
from sqlalchemy import func


class AdminUsersInfoController:
	def __init__(self,UserDAO,TimeValidatedDAO):
		self.User = UserDAO
		self.TimeValidated = TimeValidatedDAO
		self.users_info = {}
		self.today = dtt.datetime.today()
		self.project_first_day_week_started = datetime(2020, 9, 28, 0, 0, 0)
		self.num_weeks = abs(self.today-self.project_first_day_week_started).days//7 + 1
		self.users_info['user_list'] = self.__calculate_total_hours_worked_by_every_user(self.project_first_day_week_started, self.today)
		self.users_info['num_weeks'] = self.num_weeks
		


	def __calculate_total_hours_worked_by_every_user(self,date1,date2):
		users_data = ''

		users_info = self.TimeValidated.query.join(self.User, self.User.username == self.TimeValidated.user_validated)\
		.with_entities(self.TimeValidated.user_validated,self.User.data_inicio,\
					self.User.data_fim,self.User.carga_horaria,func.sum(self.TimeValidated.duration).label('sum_duration'))\
		.filter(self.TimeValidated.time_validated >= func.str_to_date(self.User.data_inicio,'%d/%m/%Y'))\
		.group_by(self.TimeValidated.user_validated).all()
		
		for user_info in users_info:
			if(len(user_info[0]) > 10 and ' ' not in user_info[0]):
				start = datetime.strptime(user_info[1].strip(),'%d/%m/%Y')
				start_monday = start - dtt.timedelta(days=start.weekday())
				
				end = datetime.strptime(user_info[2].strip(),'%d/%m/%Y')

				first_week_workload = user_info[3] - (start.weekday()*user_info[3]/5)
				first_week_workload = first_week_workload if first_week_workload > 0 else 0
				last_week_workload = (end.weekday()+1)*(user_info[3]/5)
				last_week_workload = last_week_workload if last_week_workload < user_info[3] else user_info[3]

				if(self.today >= end):
					num_weeks = abs(end-start_monday).days//7
				else:
					last_week_workload = 0
					num_weeks = abs(self.today-start_monday).days//7 + 1
					
					
				total_hours = float(user_info[-1])/3600
				start = datetime.strftime(start,'%d/%m/%Y')
				end = datetime.strftime(end,'%d/%m/%Y')
				if(user_info[0] == 'marinaaluisio@yahoo.com.br'):
					print('start '+str(start),'end '+str(end),'total_hours '+str(total_hours),'carga_horaria'+ str(user_info[3]),
					'num_weeks'+str(num_weeks),'first_week_workload'+str(first_week_workload),start_monday)
				users_data += u'{},{},{},{:.2f},{:.2f},{},{},{},{};'.format(user_info[0],start,end,
												total_hours,total_hours,user_info[3],num_weeks,first_week_workload,last_week_workload)
		
		return users_data





