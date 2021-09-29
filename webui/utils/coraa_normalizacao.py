import os
import pandas as pd
import re
import argparse
from num2words import num2words

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÇÃÀÁÂÊÉÍÓÔÕÚÛabcdefghijklmnopqrstuvwxyzçãàáâêéíóôõũúû1234567890%\-\n/\\ "

exp_let = ['a', 'bê', 'cê', 'dê', 'e', 'éfe', 'gê', 'agá', 'i', 'jota', 'cá', 'éle', 'eme', 'ene', 'o', 'pê', 'quê', 'érre',
           'ésse', 'tê', 'u', 'vê', 'dáblio', 'xis', 'ípsilom', 'zê', 'c cedilha']

parser = argparse.ArgumentParser()
parser.add_argument('--in_dir', default="../sentencas/")
parser.add_argument('--out_dir', default="../sentencas/normalizadas/")
parser.add_argument('--txt_file', default="./webui/utils/siglas.txt")

args = parser.parse_args()

in_dir = args.in_dir
out_dir = args.out_dir
txt_file = args.txt_file

# Lê arquivo com siglas e retorna uma lista com elas
with open(txt_file, 'r') as tf:
    siglas = tf.read().splitlines()


def contains_num(s):
    return any(i.isdigit() for i in s)


def normalize(text):
    # éh, eh
    filled_pause_eh = ["éh", "ehm", "ehn", "he", "éhm", "éhn", "hé"]
    # uh, hum, hm, uhm
    filled_pause_uh = ["hum", "hm", "uhm", "hu", "uhn"]
    # uhum, aham
    filled_pause_aham = ["uhum", "uhun", "unhun", "unhum", "umhun",
                         "umhum", "hunhun", "humhum", "hanhan", "ahan", "uhuhum"]
    # ah, hã, ãh, ã
    filled_pause_ah = ["hã", "ãh", "ã", "ah", "ahn", "han", "ham"]
    if text == "$$$":
        return '###'
    elif text == "@@@":
        return '###'

    # Remove marcas de truncamento (\)
    elif '/' in text:
        text = '###'
        return text

    # Remove qualquer caractere fora do alfabeto
    text = re.sub("[^{}]".format(alphabet), '', text)

    # Converte maiúsculas para minúsculas
    text = text.lower()

    # Remove hífens
    text = re.sub('\-+', " ", text)

    # Remove espaços múltiplos
    text = re.sub(' +', ' ', text)

    # Remove primeiro caractere da string se é um espaço
    if text[0] == ' ':
        text = text[1:]

    # Separa o texto em palavras e itera por elas
    words = text.split(' ')
    new_words = []
    for word in words:
        if word == '' or word == ' ':
            continue

        if word == "hhh":
            continue

        # Substitui ehhhhhh por eh e afins
        word = re.sub("h+", "h", word)

        if word in filled_pause_eh:
            word = "eh"

        elif word in filled_pause_uh:
            word = "uh"

        elif word in filled_pause_aham:
            word = "aham"

        elif word in filled_pause_ah:
            word = "ah"

        # Expande siglas
        if word in siglas:
            sigla_exp = ""
            for l in word:
                if l == 'ç':
                    sigla_exp = sigla_exp + exp_let[-1]
                else:
                    sigla_exp = sigla_exp + exp_let[ord(l) - 97]
            word = sigla_exp

        # Substitui 33% por 33 por cento e afins
        word = re.sub("\d+[%]", lambda x: x.group()+" por cento", word)
        word = re.sub("%", "", word)

        # Trata casos como 5o
        word = re.sub("\d+[o]{1}", lambda x: num2words((x.group()
                                                        [:-1]), to='ordinal', lang='pt_BR'), word)
        # Trata casos como 5a, convertendo para o ordinal masculino primeiramente
        ref = word
        word = re.sub("\d+[a]{1}", lambda x: num2words((x.group()
                                                        [:-1]), to='ordinal', lang='pt_BR'), word)
        # Se ocorreu match com ordinal feminino e foi convertido para o masculino, separamos a nova frase e trocamos os 'o's finais por 'a's
        if word != ref:
            segs = word.split(' ')
            word = ''
            for seg in segs:
                word = word + seg[:-1] + 'a' + ' '
            # Elimina o espaço adicional da última iteração
            word = word[:-1]

        if contains_num(word):
            segs = word.split(' ')
            word = ''
            for seg in segs:
                if seg.isnumeric():
                    seg = num2words(seg, lang='pt_BR')
                word = word + seg + ' '
            # Elimina o espaço adicional da última iteração
            word = word[:-1]
        new_words.append(word)

    # Reconstrói texto com palavras alteradas
    text = ''
    for new_word in new_words:
        # print(new_word)
        text = text + new_word + ' '

    # Elimina o espaço adicional da última iteração
    text = text[:-1]

    return text


# files = ["metadata_dev.csv",
#          "metadata_test.csv",
#          "metadata_train.csv"]

# # Itera pelos arquivos do diretório
# for f in files:
#     # Lê cada csv para um dataframe do pandas
#     csv_file = pd.read_csv(in_dir+f)

#     # Aplica a função de normalização para a coluna de texto do dataframe
#     csv_file['text'] = csv_file['text'].astype(str)
#     csv_file['text'] = csv_file['text'].apply(normalize)

#     # Escreve o dataframe com o texto normalizado para um novo arquivo csv
#     csv_file.to_csv(out_dir+f.replace(".csv", "_normalized.csv"), index=False)
