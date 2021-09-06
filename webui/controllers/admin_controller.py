import os


class AdminController:
    def generate_csv(self):
        # trocar path pelo o path do seu python quando for testar
        # os.system("/home/utf/miniconda4/bin/python3 ./webui/utils/generate_csv.py &")
        os.system("python ./webui/utils/generate_csv.py &")
