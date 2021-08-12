import pandas as pd


indigenas = pd.read_csv("./webui/utils/indigenas.csv", header=None)
portugueses = pd.read_csv("./webui/utils/portugueses.csv", header=None)

def check_variety(file_path):
	if(file_path in indigenas.values):
		return "pt_other"

	if(file_path in portugueses.values):
		return "pt_pt"

	return "pt_br"





