import os
import pandas as pd
import numpy as np
import librosa
import scipy.io.wavfile
from datetime import datetime


def create_new_folder_of_dataset(path):
    os.mkdir(pasta)


def copy_wavs_to_the_correct_folder():
    print("Export--", "A cópia acabou",
          "--{}".format(datetime.now().strftime("%H:%M:%S")))
    error_list = []
    SAMPLE_RATE = 16000

    TEST_CSV = "metadata_test.csv"
    TRAIN_CSV = "metadata_train.csv"
    DEV_CSV = "metadata_dev.csv"

    TEST_FOLDER = "test"
    TRAIN_FOLDER = "train"
    DEV_FOLDER = "dev"

    CSV_BASE_PATH = "./static/Dataset/export-v2/"
    WAVS_SAVE_PATH = "./static/Dataset/export-v2/wavs/"
    ORIGINAL_WAVAS_PATH = "./static/Dataset/"

    TEST_CSV_PATH = os.path.join(CSV_BASE_PATH, TEST_CSV)
    TRAIN_CSV_PATH = os.path.join(CSV_BASE_PATH, TRAIN_CSV)
    DEV_CSV_PATH = os.path.join(CSV_BASE_PATH, DEV_CSV)

    TEST_FOLDER_PATH = os.path.join(WAVS_SAVE_PATH, TEST_FOLDER)
    TRAIN_FOLDER_PATH = os.path.join(WAVS_SAVE_PATH, TRAIN_FOLDER)
    DEV_FOLDER_PATH = os.path.join(WAVS_SAVE_PATH, DEV_FOLDER)

    dev = [DEV_CSV_PATH, DEV_FOLDER_PATH]
    test = [TEST_CSV_PATH, TEST_FOLDER_PATH]
    train = [TRAIN_CSV_PATH, TRAIN_FOLDER_PATH]

    for dataset_info in [dev, test, train]:
        dataframe = pd.read_csv(dataset_info[0], sep='|')
        for index, line in dataframe.iterrows():
            wav_path = os.path.join(ORIGINAL_WAVAS_PATH, line['file_path'])
            file_path_without_data = line["file_path"][5:]
            new_wav_path = os.path.join(
                dataset_info[1], file_path_without_data)
            new_corpus_folder = '/'.join(new_wav_path.split('/')[:-1])
            os.mkdir(new_corpus_folder) if not os.path.isdir(
                new_corpus_folder) else None
            if(not os.path.isfile(new_wav_path)):
                try:
                    y, sr = librosa.load(wav_path, sr=SAMPLE_RATE)
                    scipy.io.wavfile.write(new_wav_path, sr, y)
                except:
                    error_list.append(line["file_path"])

    if(len(error_list) > 0):
        print("Erros durante a cópia")
        print(error_list)
    print("Export--", "A cópia acabou",
          "--{}".format(datetime.now().strftime("%H:%M:%S")))


copy_wavs_to_the_correct_folder()
