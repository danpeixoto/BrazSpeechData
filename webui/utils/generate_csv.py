#!/home/utf/miniconda3/bin/python3
import pymysql
import json
import pandas as pd
import re
from zipfile import ZipFile



alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÇÃÀÁÂÊÉÍÓÔÕÚÛabcdefghijklmnopqrstuvwxyzçãàáâêéíóôõũúû1234567890%\-\n/\\ "

DB_PASSWORD = ''
DB_DATABASE = ''
DB_USER = ''
DB_HOST = ''
CSV_SAVE_PATH = "./static/Dataset/export-v2/"


dev_inquiries = { 'alip': [(5101, 5611), (69594, 69901), (90223, 91256), (62920, 63181)],
				'nurc': ['NURC_RE_D2_026', 'NURC_RE_DID_012', 'NURC_RE_EF_171'],
				'ted': ['Afx_N1ce6_0', 'A56feDb1UF4', 'hXMU0sw9foQ', 'A-c8_6wy5YM', 'a-q3uOApnCM', 'a-8Sf1hUtBk', 'a0OumyN805Q', 'A_iVo-GilAo'],
				'coral': ['bfamcv01',
						  'bfamcv02',
						  'bfamcv03',
						  'bfamcv04',
						  'bfamcv05',
						  'bfamcv07',
						  'bfamcv08',
						  'bfamcv13',
						  'bfamcv15',
						  'bfamcv17',
						  'bfamcv18',
						  'bfamcv23',
						  'bfammn01',
						  'bfammn03',
						  'bfammn04',
						  'bfammn05',
						  'bfammn06',
						  'bfammn08'],
				'sp': [(62924, 64782), (58030, 59427)]
			  }


test_inquiries = { 'alip': [(42389, 43336), (80027, 80670), (3159,3704), (9630,9925), (50734,51374), (64387,64745), (62514,62918), (39927,40392), (44171,44470)],
				 'nurc': ['NURC_RE_D2_215', 'NURC_RE_DID_051', 'NURC_RE_EF_332', 'NURC_RE_D2_287', 'NURC_RE_DID_029', 'NURC_RE_EF_271'],
				 'ted': ['AxwfIffqIXo', 'aETOz3IGfG0', 'aXZ9Cb9ffE8', 'A0dfeodJL8Q', 'A4wi3jmf9uY', 'a4ZFKFLLORE', 'A04wa_SH1WM', 'A1yGXAJx-x8', 'a8gyl6MPHsI', 'Ab5xNf5VoEc', 'a9qsp7l5C3o', 'a24A8MyzR2Y', 'AB8_pog3Lt8', 'aai3QcbLetk'],
				 'coral': ['bfamcv20',
						   'bfammn09',
						   'bfammn10',
						   'bfammn11',
						   'bfammn12',
						   'bfammn15',
						   'bfammn16',
						   'bfammn17',
						   'bfammn18',
						   'bfammn19',
						   'bfammn20',
						   'bfammn22',
						   'bfammn23',
						   'bfammn24',
						   'bfammn25',
						   'bfammn26',
						   'bfammn27',
						   'bfammn28',
						   'bfammn29',
						   'bfammn30',
						   'bfammn31',
						   'bfammn32',
						   'bfammn33',
						   'bfammn34',
						   'bfammn35'],
				 'sp': [(44928, 46578), (47450,49028), (70578,71973), (42881,43677)]
			   }


def get_destination(line):

	global dev_inquiries, test_inquiries

	if '/alip/' in line['file_path'].lower():

		file_path_id = int(os.path.basename(line['file_path']).replace('_alip_.wav', ''))

		for interval in dev_inquiries['alip']:
			if(file_path_id >= interval[0] and file_path_id <= interval[1]):
				return 'dev'
		for interval in test_inquiries['alip']:
			if(file_path_id >= interval[0] and file_path_id <= interval[1]):
				return 'test'
		return 'train'

	elif '/ted/' in line['file_path'].lower():

		for id in dev_inquiries['ted']:
			if id in line['file_path']:
				return 'dev'
		for id in test_inquiries['ted']:
			if id in line['file_path']:
				return 'test'
		return 'train'

	elif '/nurc_re/' in line['file_path'].lower():

		for id in dev_inquiries['nurc']:
			if id in line['file_path']:
				return 'dev'
		for id in test_inquiries['nurc']:
			if id in line['file_path']:
				return 'test'
		return 'train'

	elif '/coral/' in line['file_path'].lower():

		for id in dev_inquiries['coral']:
			if id in line['file_path']:
				return 'dev'
		for id in test_inquiries['coral']:
			if id in line['file_path']:
				return 'test'
		return 'train'

	elif '/sp2010/' in line['file_path'].lower():

		file_path_id = int(os.path.basename(line['file_path']).replace('_sp_.wav', '').replace('data/', '').replace('wavs/SP2010/', ''))

		for interval in dev_inquiries['sp']:
			if(file_path_id >= interval[0] and file_path_id <= interval[1]):
				return 'dev'
		for interval in test_inquiries['sp']:
			if(file_path_id >= interval[0] and file_path_id <= interval[1]):
				return 'test'
		else:
			return 'train'

	else:
		RuntimeError(" File não pertencente a nenhum dos datasets estabelecidos: "+line['file_path'])


def filter_dataset(data_df):

	df_output = []
	
	for index, line in data_df.iterrows():
		text = line['text']
		text = re.sub("[^{}]".format(alphabet), '', text)

		text = text.lower()
		text = re.sub(' +', ' ', text)

		if not len(text.replace(" ", '')):
			continue

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
		
	return df_output


def split_dataset_on_train_test_eval(dataframe):

	# buffer de linhas----------------------------
	final_dev = []
	final_train = []
	final_test = []
	failed_files = []

	# loop principal-------------------------------
	for index, line in dataframe.iterrows():
		data_dict = { "text": line['text'], "file_path": line['file_path'], "task": line['task'], "valid_score": line['valid_score'], "invalid_score": line['invalid_score'], "dataset": line['dataset'], "accent": line['accent'], "speech_form": line['speech_form']}
		try:
			dest = get_destination(line)
			if(dest == 'dev'):
				final_dev.append(data_dict)
			elif(dest == 'test'):
				final_test.append(data_dict)
			else:
				final_train.append(data_dict)

		except Exception as e:
			failed_files.append(line['file_path'])
			# print(e)


	


	# escrevendo arquivos----------------------------------------

	train_df = pd.DataFrame.from_dict(final_train, orient='columns')
	# train_df.to_csv(out_train, sep=',', encoding='utf-8', header=True, index=False)
	# print("Train samples saved in: ", out_train)

	dev_df = pd.DataFrame.from_dict(final_dev, orient='columns')
	# dev_df.to_csv(out_dev, sep=',', encoding='utf-8', header=True, index=False)
	# print("Dev samples saved in: ", out_dev)


	test_df = pd.DataFrame.from_dict(final_test, orient='columns')
	# test_df.to_csv(out_test, sep=',', encoding='utf-8', header=True, index=False)
	# print("Test samples saved in: ", out_test)

	failed_df = pd.DataFrame.from_dict(failed_files, orient='columns')
	# failed_df.to_csv(out_failed, sep=',', encoding='utf-8', header=True, index=False)

	return train_df,dev_df,test_df,failed_df


def generate_csv():
	conn = pymysql.connect(host=DB_HOST,user=DB_USER,password = DB_PASSWORD,db=DB_DATABASE)

	cur = conn.cursor()

	cur.execute('SELECT text,file_path,task,valids_user1,valids_user2,valids_user3,invalid_user1,invalid_user2,invalid_user3 FROM Dataset WHERE text NOT LIKE \'%#%\' AND number_validated >= 1 AND data_gold = 0 AND file_path NOT LIKE \'%wpp%\'')

	output = cur.fetchall()

	compression_opts = dict(method='zip',archive_name = 'resultado.csv')
	data_df = pd.DataFrame(output,columns=['text','file_path','task','valids_user1','valids_user2','valids_user3','invalid_user1','invalid_user2','invalid_user3'])

	data_df['valid_score'] = 0
	data_df['invalid_score'] = 0
	
	df_output = filter_dataset(data_df)

	final_df = pd.DataFrame.from_dict(df_output, orient='columns')


	train_df,dev_df,test_df,failed_df = split_dataset_on_train_test_eval(final_df)


	train_df.to_csv(CSV_SAVE_PATH+"metadata_train.csv", sep=',', encoding='utf-8', header=True, index=False)
	dev_df.to_csv(CSV_SAVE_PATH+"metadata_dev.csv", sep=',', encoding='utf-8', header=True, index=False)
	test_df.to_csv(CSV_SAVE_PATH+"metadata_test.csv", sep=',', encoding='utf-8', header=True, index=False)
	failed_df.to_csv(CSV_SAVE_PATH+"failed_files.txt", sep=',', encoding='utf-8', header=True, index=False)

	# final_df.to_csv('dataset.zip',encoding='utf-8', index=False,sep='|',compression=compression_opts)


def compress_all_csv_in_one_file():
	with ZipFile(CSV_SAVE_PATH+"dataset.zip","w") as zipObj:
		zipObj.write(CSV_SAVE_PATH+"metadata_train.csv","metadata_train.csv")
		zipObj.write(CSV_SAVE_PATH+"metadata_test.csv","metadata_test.csv")
		zipObj.write(CSV_SAVE_PATH+"metadata_dev.csv","metadata_dev.csv")
		zipObj.write(CSV_SAVE_PATH+"failed_files.txt","failed_files.txt")

with open('./common/enviroment.json') as json_file:
	JSON = json.load(json_file)
	DB_PASSWORD = JSON['dbPassword']
	DB_DATABASE = JSON['dbDatabase']
	DB_USER = JSON['dbUser']
	DB_HOST = JSON['dbHost']
	generate_csv()
	compress_all_csv_in_one_file()


