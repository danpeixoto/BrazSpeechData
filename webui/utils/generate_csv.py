#!/home/utf/miniconda3/bin/python3
from datetime import datetime
from numpy.testing._private.utils import raises
import pymysql
import json
import pandas as pd
import re
import check_audio_variety as cav
from zipfile import ZipFile
import hashlib
import coraa_normalizacao
import os

# For easy navigation use |\


# |\ Global variables

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÇÃÀÁÂÊÉÍÓÔÕÚÛabcdefghijklmnopqrstuvwxyzçãàáâêéíóôõũúû1234567890%\-\n/\\ "

# DB variables receive values from the enviroment.json
DB_PASSWORD = ''
DB_DATABASE = ''
DB_USER = ''
DB_HOST = ''
# path based on where the script is called
CSV_SAVE_PATH = "./static/Dataset/export-v2/"
FAILED_FILES = []

# dev_inquiries_old = {'alip': [(5101, 5611), (69594, 69901), (90223, 91256), (62920, 63181)],
#                  'nurc': ['NURC_RE_D2_026', 'NURC_RE_DID_012', 'NURC_RE_EF_171'],
#                  'ted': ['Afx_N1ce6_0',
#                          'A56feDb1UF4',
#                          'hXMU0sw9foQ',
#                          'A-c8_6wy5YM',
#                          'a-q3uOApnCM',
#                          'a-8Sf1hUtBk',
#                          'a0OumyN805Q',
#                          'A_iVo-GilAo'],
#                  'coral': ['bfamcv01',
#                            'bfamcv02',
#                            'bfamcv03',
#                            'bfamcv04',
#                            'bfamcv05',
#                            'bfamcv07',
#                            'bfamcv08',
#                            'bfamcv13',
#                            'bfamcv15',
#                            'bfamcv17',
#                            'bfamcv18',
#                            'bfamcv23',
#                            'bfammn01',
#                            'bfammn03',
#                            'bfammn04',
#                            'bfammn05',
#                            'bfammn06',
#                            'bfammn08'],
#                  'sp': [(62924, 64782), (58030, 59427)]
#                  }
dev_inquiries = {'alip': [(5101, 5611), (69594, 69901), (90223, 91256), (62920, 63181)],
                 'nurc': ['NURC_RE_D2_026', 'NURC_RE_DID_012', 'NURC_RE_EF_171'],
                 'ted': ['Afx_N1ce6_0', 'A56feDb1UF4', 'hXMU0sw9foQ', 'A-c8_6wy5YM', 'a-q3uOApnCM', 'a-8Sf1hUtBk', 'a0OumyN805Q', 'A_iVo-GilAo', '_1yNRrSf0BU', '7J-Z-k0ewDI', '7LqV2GVcaEw', '7o7FDCU_-zE', '7oes6OulbYg', '7pUjNZKckrY', '7PYKXMC1WPE', '7slENTYU2gU', '7WZRxfmeuEY', '7XJCLa1xWfk', '7zzRywQCo-Y', '81ZFuEHRfB8', '86OG8yN9muk', '_8iCvZ2WRQU', '8iWtTBR4kYo', '8lHrmpqWq_4', '9LJ-g9If8PY', '9QTNqR_vhV0', '9t9GshqRQZc', '9wNDowlBmo0', '9YU6zcr2z28', 'a0mXmqCcoso', 'a5Ua7Xq9I6Y', 'a6vF8ywAknk', 'a87BeNA3xVI'],
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

# test_inquiries_old = {'alip': [(42389, 43336), (80027, 80670), (3159, 3704), (9630, 9925), (50734, 51374), (64387, 64745), (62514, 62918), (39927, 40392), (44171, 44470)],
#                   'nurc': ['NURC_RE_D2_215', 'NURC_RE_DID_051', 'NURC_RE_EF_332', 'NURC_RE_D2_287', 'NURC_RE_DID_029', 'NURC_RE_EF_271'],
#                   'ted': ['AxwfIffqIXo', 'aETOz3IGfG0', 'aXZ9Cb9ffE8', 'A0dfeodJL8Q', 'A4wi3jmf9uY', 'a4ZFKFLLORE', 'A04wa_SH1WM', 'A1yGXAJx-x8', 'a8gyl6MPHsI', 'Ab5xNf5VoEc', 'a9qsp7l5C3o', 'a24A8MyzR2Y', 'AB8_pog3Lt8', 'aai3QcbLetk'],
#                   'coral': ['bfamcv20',
#                             'bfammn09',
#                             'bfammn10',
#                             'bfammn11',
#                             'bfammn12',
#                             'bfammn15',
#                             'bfammn16',
#                             'bfammn17',
#                             'bfammn18',
#                             'bfammn19',
#                             'bfammn20',
#                             'bfammn22',
#                             'bfammn23',
#                             'bfammn24',
#                             'bfammn25',
#                             'bfammn26',
#                             'bfammn27',
#                             'bfammn28',
#                             'bfammn29',
#                             'bfammn30',
#                             'bfammn31',
#                             'bfammn32',
#                             'bfammn33',
#                             'bfammn34',
#                             'bfammn35'],
#                   'sp': [(44928, 46578), (47450, 49028), (70578, 71973), (42881, 43677)]
#                   }

test_inquiries = {'alip': [(42389, 43336), (80027, 80670), (3159, 3704), (9630, 9925), (50734, 51374), (64387, 64745), (62514, 62918), (39927, 40392), (44171, 44470)],
                  'nurc': ['NURC_RE_D2_215', 'NURC_RE_DID_051', 'NURC_RE_EF_332', 'NURC_RE_D2_287', 'NURC_RE_DID_029', 'NURC_RE_EF_271'],
                  'ted': ['AxwfIffqIXo', 'aETOz3IGfG0', 'aXZ9Cb9ffE8', 'A0dfeodJL8Q', 'A4wi3jmf9uY', 'a4ZFKFLLORE', 'A04wa_SH1WM', 'A1yGXAJx-x8', 'a8gyl6MPHsI', 'Ab5xNf5VoEc', 'a9qsp7l5C3o', 'a24A8MyzR2Y', 'AB8_pog3Lt8', 'aai3QcbLetk', 'a8bFAd--TMo', 'ACsrAr078s0', 'aE1GNHkyaSA', 'aejhRTw0D0g', 'AeyUze9hChw', 'afswsiDBB6Q', 'aIndPtZGDz4', 'air_84KLk0E', 'aj6_ZRuUm04', 'akDoEll2QGk', 'akUTDpfWZUk', 'An42G86kZEk', 'AP-bmCOGOH8', 'AqQJz1j_4rY', 'AS_w0fiMQgc', 'av2bOcV8yPU', 'axJSBG9DNKQ', 'AxOK90gji-o', 'b321AmixDeA', 'B32hWJqIyQM', 'b7DAWzoV1sE', 'b8PrusSGUn4', 'BaIwFh3geLU', 'bAO--a13WZ4', 'Bb0bY4o5y9E', 'BbqOyyKXaqY', 'bbqqsRE_ZFc', 'Bc7Sv7AE44s', 'bdGjUmau5Kg', 'bDGSJ_HNU14', 'BD_LL73Yjic', 'BdLU9I4JDAA', 'bDqGZT3OTgw', 'bE-4E1eUk6o', 'bHXkqtjb0O0', 'BILl-ziMwDY', 'bl4wxKurOvM', 'Bm3S2BiS-2Y', 'BMZ-NF79hwE', 'bnj979xWDTU', 'bnoorgXkmWE', 'bo3_ncIpin8', 'Bqon4_rKigs', 'bRSGaB-iZck', 'bRVYfip4ErU', 'Bs1bmBCCMas', 'bsqJmqNPUI0', '__BtfBTQJoM', 'BvlRNXbCD5M', 'C6wasqRsDug', 'c9itqVKg8gM', 'Cb1o0K5V11I', 'cCbKdmiiMRg', 'cFFFwDmfOf8', 'CGaxtJzpEa0', 'Ci7zHYozq8o', 'cix55h305q0', 'CJma5FsE7Ig', 'CKOvfEpgc6k', 'CkVQUa2xig8', 'CKY8NHaWmXg', 'CLxeqgtKWs0', 'C_m4EUdcghY', 'CMEwr5RuvOY', 'CnlGkxksy_g', 'CR02Z-wDwNs', 'cVZSicAvgAg', 'cW7w5NCenxI', 'cxeN1XIP8Fs', 'cYrgbptYcho', 'D1hcRxpYCIs'],
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
                  'sp': [(44928, 46578), (47450, 49028), (70578, 71973), (42881, 43677)]
                  }

# |\ Get audio correct file (train,test,eval,fail)


def get_destination(line):
    """Gets file destination.

        Set the correct destination to the line and raises an error if the 
        line does not appear in any corpus.

        Args: 
            line         : dict containg one row of the dataframe.
        Returns:
            string       : a string containing the correct file destination
        Raises:
            RuntimeError : File not found in the datasets
    """
    global dev_inquiries, test_inquiries

    if '/alip/' in line['file_path'].lower():
        # convert the file_path to integer (id)
        file_path_id = int(os.path.basename(
            line['file_path']).replace('_alip_.wav', ''))
        for interval in dev_inquiries['alip']:
            if(file_path_id >= interval[0] and file_path_id <= interval[1]):
                return 'dev'
        for interval in test_inquiries['alip']:
            if(file_path_id >= interval[0] and file_path_id <= interval[1]):
                return 'test'
        return 'train'

    elif '/ted_' in line['file_path'].lower():

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
    elif '/sp/' in line['file_path'].lower():
        # convert the file_path to integer (id)
        file_path_id = int(os.path.basename(line['file_path']).replace(
            '_sp_.wav', '').replace('data/', '').replace('wavs/SP2010/', ''))
        for interval in dev_inquiries['sp']:
            if(file_path_id >= interval[0] and file_path_id <= interval[1]):
                return 'dev'
        for interval in test_inquiries['sp']:
            if(file_path_id >= interval[0] and file_path_id <= interval[1]):
                return 'test'
        return 'train'
    # Raise an error if the line is not present in any corpus
    raise RuntimeError(
        "File não pertencente a nenhum dos datasets estabelecidos: "+line['file_path'])

# |\ Utils


def sum_two_int_strings(a, b="1"):
    return str(int(a)+int(b))

# |\ Update audio characteristics


def upadate_audio_characteristics(valids_user, c1, c2, c3, c4, c5):
    one, two, three, four, five = re.sub('[\[\]]', '', valids_user).split(',')
    if "1" in one:
        c1 = sum_two_int_strings(c1)
    if "2" in two:
        c2 = sum_two_int_strings(c2)
    if "3" in three:
        c3 = sum_two_int_strings(c3)
    if "4" in four:
        c4 = sum_two_int_strings(c4)
    if "5" in five:
        c5 = sum_two_int_strings(c5)
    return c1, c2, c3, c4, c5
# |\ Filter the dataset


def filter_dataset(data_df):
    """Filters a dataset.

        Remove all incorrect files from the dataset using Bruno's normalization,
        some rules specific to annotation and some rules specific to 
        transcription.

        Args: 
            data_df   : pandas dataframe containing rows from the database.
        Returns:
            df_output : list of dicts containing only valid files.
        Raises:
    """
    df_output = []

    for index, line in data_df.iterrows():
        has_no_identified_problem = 0  # valids_user [1,0,0,0,0]
        has_filled_pause = 0  # valids_user [0,2,0,0,0]
        has_hesitation = 0  # valids_user [0,0,3,0,0]
        has_noise_or_low_voice = 0  # valids_user [0,0,0,4,0]
        has_second_voice = 0  # valids_user [0,0,0,0,5]
        text = line['text']
        text = re.sub("[^{}]".format(alphabet), '', text)

        text = text.lower()
        text = re.sub(' +', ' ', text)
        # Removes files that have *, $ or @ in the text
        if (("@" in text) or ("$" in text) or ("*" in text)):
            FAILED_FILES.append(line['file_path'])
            continue
        # Normalize the text using Bruno's script
        text = coraa_normalizacao.normalize(text)

        if ((not len(text.replace(" ", ''))) or ("#" in text)):
            FAILED_FILES.append(line['file_path'])
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
            has_no_identified_problem, has_filled_pause, has_hesitation, has_noise_or_low_voice, has_second_voice = upadate_audio_characteristics(
                line['valids_user1'], has_no_identified_problem, has_filled_pause, has_hesitation, has_noise_or_low_voice, has_second_voice)
        if line['valids_user2'] != '' and line['valids_user2'] != 'None':
            valid_score += 1
            has_no_identified_problem, has_filled_pause, has_hesitation, has_noise_or_low_voice, has_second_voice = upadate_audio_characteristics(
                line['valids_user2'], has_no_identified_problem, has_filled_pause, has_hesitation, has_noise_or_low_voice, has_second_voice)
        if line['valids_user3'] != '' and line['valids_user3'] != 'None':
            valid_score += 1
            has_no_identified_problem, has_filled_pause, has_hesitation, has_noise_or_low_voice, has_second_voice = upadate_audio_characteristics(
                line['valids_user3'], has_no_identified_problem, has_filled_pause, has_hesitation, has_noise_or_low_voice, has_second_voice)

        # This rule was made due to inconsistencies in the database.
        if line['task'] == 1 and (not '/CORAL/' in line['file_path']) and (not '/NURC_RE/' in line['file_path']) and (not '/sp/' in line['file_path']):
            line['task'] = 'transcription'
            has_no_identified_problem = has_filled_pause = has_hesitation = has_second_voice = has_noise_or_low_voice = None
            valid_score = invalid_score = 0
        elif line['task'] == 0:
            line['task'] = 'annotation'
        else:
            line['task'] = 'annotation_and_transcription'

        # Remove files that were invalidated more than validated. This rule only applies to audios of annotation
        if(valid_score <= invalid_score and (line['task'] == 'annotation' or line['task'] == 'annotation_and_transcription')):
            FAILED_FILES.append(line['file_path'])
            continue

        variety = "pt_br"

        if '/alip/' in line['file_path']:
            dataset = 'ALIP'
            accent = 'São Paulo (int.)'
            speech_genre = 'Interview or Dialogue'
            speech_style = 'Spontaneous Speech'
        elif '/CORAL/' in line['file_path']:
            dataset = 'C-ORAL-BRASIL I'
            accent = 'Minas Gerais'
            speech_genre = 'Monologue or Dialogue or Conversation'
            speech_style = 'Spontaneous Speech'
        elif '/NURC_RE/' in line['file_path']:
            dataset = 'NURC-Recife'
            accent = 'Recife'
            speech_genre = 'Dialogue or Interview or Conference and Class Talks'
            speech_style = 'Spontaneous Speech'
            if('/NURC_RE_EF/' in line['file_path']):
                speech_style = 'Prepared Speech'
        elif '/sp/' in line['file_path']:
            dataset = 'SP2010'
            accent = 'São Paulo (cap.)'
            speech_genre = 'Conversation or Interview or Reading'
            speech_style = 'Spontaneous and Read Speech'
        elif '/Ted_' in line['file_path']:
            dataset = 'TEDx Talks'
            accent = 'Misc.'
            speech_genre = 'Stage Talks'
            variety = cav.check_variety(line['file_path'].split("/")[2][:-9])
            # Remove files that are from indigenous people
            if(not variety):
                FAILED_FILES.append(line['file_path'])
                continue
            speech_style = 'Prepared Speech'

        # data_dict = {"text": text, "file_path": line['file_path'], "task": line['task'], "up_votes": valid_score, "down_votes": invalid_score,
            #  "dataset": dataset, "accent": accent, "speech_genre": speech_genre, "speech_style": speech_style, "variety": variety}
        data_dict = {"file_path": line['file_path'], "task": line['task'], "variety": variety, "dataset": dataset, "accent": accent,
                     "speech_genre": speech_genre, "speech_style": speech_style,
                     "up_votes": valid_score, "down_votes": invalid_score, "has_hesitation": has_hesitation,
                     "has_filled_pause": has_filled_pause, "has_noise_or_low_voice": has_noise_or_low_voice,
                     "has_second_voice": has_second_voice, "has_no_identified_problem": has_no_identified_problem, "text": text}
        df_output.append(data_dict)

    return df_output

# |\ Split the dataset


def split_dataset_on_train_test_eval(dataframe):
    """Splits a dataframe.

        Split CORAA dataset into train,test and eval datasets.
        Args:
            dataframe : pandas dataframe containing only valid rows.
        Returns:
            train_df  : dataframe containing rows for training.
            dev_df    : dataframe containing rows for evaluation.
            test_df   : dataframe containing rows for testing.
            failed_df : dataframe containing audio paths that do not appear 
                        in any corpus.
        Raises:
    """

    final_dev = []
    final_train = []
    final_test = []

    # Loop all rows and place them in it's correct CSV
    for index, line in dataframe.iterrows():
        data_dict = {"file_path": line['file_path'], "task": line['task'], "variety": line['variety'], "dataset": line['dataset'], "accent": line['accent'],
                     "speech_genre": line['speech_genre'], "speech_style": line['speech_style'],
                     "up_votes": line['up_votes'], "down_votes": line['down_votes'], "votes_for_hesitation": line['has_hesitation'],
                     "votes_for_filled_pause": line['has_filled_pause'], "votes_for_noise_or_low_voice": line['has_noise_or_low_voice'],
                     "votes_for_second_voice": line['has_second_voice'], "votes_for_no_identified_problem": line['has_no_identified_problem'], "text": line['text']}
        try:
            dest = get_destination(line)
            if(dest == 'dev'):
                final_dev.append(data_dict)
            elif(dest == 'test'):
                final_test.append(data_dict)
            else:
                final_train.append(data_dict)

        except Exception as e:
            FAILED_FILES.append(line['file_path'])
            print(e)

    print(len(FAILED_FILES))

    train_df = pd.DataFrame.from_dict(final_train, orient='columns')

    dev_df = pd.DataFrame.from_dict(final_dev, orient='columns')

    test_df = pd.DataFrame.from_dict(final_test, orient='columns')

    failed_df = pd.DataFrame.from_dict(FAILED_FILES, orient='columns')

    return train_df, dev_df, test_df, failed_df

# |\ Generate all CSVs (main function)


def generate_csv():
    """Generates many CSVs.

        Generate all CVSs of CORAA.

        Args:
        Returns:
        Raises:
    """
    conn = pymysql.connect(host=DB_HOST, user=DB_USER,
                           password=DB_PASSWORD, db=DB_DATABASE)
    cur = conn.cursor()

    # The query below must only return rows with data_gold equals 0
    cur.execute('SELECT text,file_path,task,valids_user1,valids_user2,valids_user3,invalid_user1,invalid_user2,invalid_user3 FROM Dataset WHERE text NOT LIKE \'%#%\' AND number_validated >= 1 AND data_gold = 0 AND file_path NOT LIKE \'%wpp%\' AND (duration <= 40 OR LENGTH(text)<=200)')

    output = cur.fetchall()

    data_df = pd.DataFrame(output, columns=['text', 'file_path', 'task', 'valids_user1',
                                            'valids_user2', 'valids_user3', 'invalid_user1', 'invalid_user2', 'invalid_user3'])

    data_df['valid_score'] = 0
    data_df['invalid_score'] = 0
    df_output = filter_dataset(data_df)

    final_df = pd.DataFrame.from_dict(df_output, orient='columns')

    train_df, dev_df, test_df, failed_df = split_dataset_on_train_test_eval(
        final_df)

    train_df.to_csv(CSV_SAVE_PATH+"metadata_train.csv", sep="|",
                    encoding='utf-8', header=True, index=False)
    dev_df.to_csv(CSV_SAVE_PATH+"metadata_dev.csv", sep="|",
                  encoding='utf-8', header=True, index=False)
    test_df.to_csv(CSV_SAVE_PATH+"metadata_test.csv", sep="|",
                   encoding='utf-8', header=True, index=False)
    failed_df.to_csv(CSV_SAVE_PATH+"failed_files.txt", sep="|",
                     encoding='utf-8', header=True, index=False)

# |\ Compress all CSVs in a zip file


def compress_all_csv_in_one_file():
    """Compresses all CSVs.

        Compress all CSVs into a zip file.

        Args:
        Returns:
        Raises:
    """
    with ZipFile(CSV_SAVE_PATH+"dataset.zip", "w") as zipObj:
        zipObj.write(CSV_SAVE_PATH+"metadata_train.csv", "metadata_train.csv")
        zipObj.write(CSV_SAVE_PATH+"metadata_test.csv", "metadata_test.csv")
        zipObj.write(CSV_SAVE_PATH+"metadata_dev.csv", "metadata_dev.csv")
        zipObj.write(CSV_SAVE_PATH+"failed_files.txt", "failed_files.txt")


# |\ Generate the CSVs and then compress them
with open('./common/enviroment.json') as json_file:
    JSON = json.load(json_file)
    DB_PASSWORD = JSON['dbPassword']
    DB_DATABASE = JSON['dbDatabase']
    DB_USER = JSON['dbUser']
    DB_HOST = JSON['dbHost']
    print("Export--", "Criação do csv começou",
          "--{}".format(datetime.now().strftime("%H:%M:%S")))
    generate_csv()
    compress_all_csv_in_one_file()
    print("Export--", "Criação do csv acabou",
          "--{}".format(datetime.now().strftime("%H:%M:%S")))
