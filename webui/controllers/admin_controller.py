import pandas as pd
from sqlalchemy import not_


class AdminController:
	def __init__(self,DatasetDAO):
		self.Dataset = DatasetDAO

	def handle_post_request(self):

		compression_opts = dict(method='zip',archive_name = 'resultado.csv')
		data = self.Dataset.query\
				.with_entities(self.Dataset.text,self.Dataset.file_path,self.Dataset.task)\
				.filter(self.Dataset.invalid_user1 == 0 , 
						not_(self.Dataset.text.ilike('%#%')),
						self.Dataset.number_validated == 1,
						self.Dataset.data_gold == 0)\
				.all()
		
		data_df = pd.DataFrame(data,columns=['text','file_path','task'])
		data_df.task[data_df.task == 0] = 'annotation'
		data_df.task[data_df.task == 1] = 'transcriptions'

		data_df.to_csv('dataset.zip',encoding='utf-8', index=False,sep='|',compression=compression_opts)
