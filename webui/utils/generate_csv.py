#!/home/utf/miniconda3/bin/python3
import pymysql
import json
import pandas as pd
import re
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÇÃÀÁÂÊÉÍÓÔÕÚÛabcdefghijklmnopqrstuvwxyzçãàáâêéíóôõũúû1234567890%\-\n/\\ "

DB_PASSWORD = ''
DB_DATABASE = ''
DB_USER = ''
DB_HOST = ''
     

def generate_csv():
	conn = pymysql.connect(host=DB_HOST,user=DB_USER,password = DB_PASSWORD,db=DB_DATABASE)

	cur = conn.cursor()

	cur.execute('SELECT text,file_path,task,valids_user1,valids_user2,valids_user3,invalid_user1,invalid_user2,invalid_user3 FROM Dataset WHERE text NOT LIKE \'%#%\' AND number_validated >= 1 AND data_gold = 0 AND file_path NOT LIKE \'%wpp%\'')

	output = cur.fetchall()

	compression_opts = dict(method='zip',archive_name = 'resultado.csv')
	data_df = pd.DataFrame(output,columns=['text','file_path','task','valids_user1','valids_user2','valids_user3','invalid_user1','invalid_user2','invalid_user3'])

	data_df['valid_score'] = 0
	data_df['invalid_score'] = 0
	df_output = []
	
	for index, line in data_df.iterrows():
		text = line['text']
		text = re.sub("[^{}]".format(alphabet), '', text)

		text = text.lower()
		text = re.sub(' +', ' ', text)

		if not len(text.replace(" ", '')):
			continue

		data_df.loc[index, 'text'] = text

		invalid_score = 0
		valid_score = 0

		if line['invalid_user1'] < 0 and not isinstance(line['invalid_user1'], str):
			invalid_score += 1
		if line['invalid_user2'] < 0 and not isinstance(line['invalid_user2'], str):
			invalid_score += 1
		if line['invalid_user3'] < 0 and not isinstance(line['invalid_user3'], str):
			invalid_score += 1
			
		if line['valids_user1'] != '' and line['valids_user1'] != 'None':
			valid_score += 1
		if line['valids_user2'] != '' and line['valids_user2'] != 'None':
			valid_score += 1
		if line['valids_user3'] != '' and line['valids_user3'] != 'None':
			valid_score += 1
		
		if line['task'] == 1:
			line['task'] = 'transcription'
		else:
			line['task'] = 'annotation'

		if '/alip/' in line['file_path']:
			dataset = 'ALIP' 
			accent = 'São Paulo (int.)'
			speech_form = 'Interview or Dialogue'
		elif '/CORAL/' in line['file_path']:
			dataset = 'C-ORAL-BRASIL I'
			accent = 'Minas Gerais'
			speech_form = 'Monologue or Dialogue or Conversation'
		elif '/NURC_RE/' in line['file_path']:
			dataset = 'NURC-Recife'
			accent = 'Recife'
			speech_form = 'Dialogue or Interview or Prepared Speech'
		elif '/sp/' in line['file_path']:
			dataset = 'SP2010'
			accent = 'São Paulo (cap.)'
			speech_form = 'Conversation or Interview or Reading'
		elif '/Ted_' in line['file_path']:
			dataset = 'TEDx Talks'
			accent = 'Misc.'
			speech_form = 'Prepared Speech'

		data_dict = { "text": line['text'], "file_path": line['file_path'], "task": line['task'], "valid_score": valid_score, "invalid_score": invalid_score, "dataset": dataset, "accent": accent, "speech_form": speech_form}
		df_output.append(data_dict)
		


	final_df = pd.DataFrame.from_dict(df_output, orient='columns')
	final_df.to_csv('dataset.zip',encoding='utf-8', index=False,sep='|',compression=compression_opts)

with open('./enviroment.json') as json_file:
	JSON = json.load(json_file)
	DB_PASSWORD = JSON['dbPassword']
	DB_DATABASE = JSON['dbDatabase']
	DB_USER = JSON['dbUser']
	DB_HOST = JSON['dbHost']
	generate_csv()


