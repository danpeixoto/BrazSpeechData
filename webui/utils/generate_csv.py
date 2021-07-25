import pymysql
import json
import pandas as pd

DB_PASSWORD = ''
DB_DATABASE = ''
DB_USER = ''
DB_HOST = ''


def generate_csv():
	conn = pymysql.connect(host=DB_HOST,user=DB_USER,password = DB_PASSWORD,db=DB_DATABASE)

	cur = conn.cursor()

	cur.execute('SELECT text,file_path,task FROM Dataset WHERE invalid_user1 = 0 AND text NOT LIKE \'%#%\' AND number_validated = 1 AND data_gold = 0')

	output = cur.fetchall()

	compression_opts = dict(method='zip',archive_name = 'resultado.csv')
	data_df = pd.DataFrame(output,columns=['text','file_path','task'])

	data_df.loc[data_df.task == 1 , 'task'] = 'transcription'
	data_df.loc[data_df.task == 0 , 'task'] = 'annotation'

	data_df.to_csv('dataset.zip',encoding='utf-8', index=False,sep='|',compression=compression_opts)

with open('./common/enviroment.json') as json_file:
	JSON = json.load(json_file)
	DB_PASSWORD = JSON['dbPassword']
	DB_DATABASE = JSON['dbDatabase']
	DB_USER = JSON['dbUser']
	DB_HOST = JSON['dbHost']
	generate_csv()


