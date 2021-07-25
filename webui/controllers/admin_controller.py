import pandas as pd
from sqlalchemy import not_
import os

class AdminController:

	def generate_csv(self):
		os.system("python ./webui/utils/generate_csv.py &")
