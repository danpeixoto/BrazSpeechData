import os


class AdminController:
    def generate_csv(self):
        # trocar path pelo o path do seu python quando for testar
        # os.system("/home/utf/miniconda3/bin/python3 ./webui/utils/generate_csv.py &")
        # os.system("python ./webui/utils/manage_dataset_export.py")
        os.system(
            "python ./webui/utils/generate_csv.py >> export.log && python ./webui/utils/copy_wavs_from_csv.py >> export.log & ")
        # os.system("/home/utf/miniconda3/bin/python3 ./webui/utils/generate_csv.py && /home/utf/miniconda3/bin/python3 ./webui/utils/copy_wavs_from_csv.py & >> export.log ")
