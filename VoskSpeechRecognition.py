import os
import re
import pandas as pd
from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import wave
import json
import winsound
import tqdm


nickname_stitch_needed = 'americans' # ЗАМЕНИТЬ ЗДЕСЬ ЗНАЧЕНИЕ НА НУЖНОЕ НАЗВАНИЕ ПАПКИ

def get_aweme_id_from_audio (filename):

    ''' Функция принимает на вход название аудиофайла из спарсенных видео
    и возвращает уникальный идентификатор видео (aweme_id).'''

    aweme_id = int (re.split ('_|.wav', filename)[1])
    return aweme_id
def stt_function (audio_file):

    ''' Для Python 3.9 и импортированной модели vosk!!!

    Функция принимает на вход название моно-wav-аудиофайла,
    расшифровывает речь на американском английском и
    записывает результат распознавания в txt-файл, название которого состоит
    из названия аудио файла + _stt.txt.

    Функция возвращает распознанный текст единой строкой.'''

    # ЗАПУСК МОДЕЛИ РАСПОЗНАВАНИЯ РЕЧИ

    SetLogLevel(0)

    if not os.path.exists("model"):
        print(
            "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit(1)

    wf = wave.open (audio_file, "rb") 
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print ("Audio file must be WAV format mono PCM.")
        exit (1)

    model = Model("model")
    rec = KaldiRecognizer(model, wf.getframerate())

    final_json = {}
    i = 0

    with open(f'{audio_file[:-4]}_stt.txt', 'a') as output:  
        print('[', file=output)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            with open(f'{audio_file[:-4]}_stt.txt', 'a') as output:
                print (rec.Result(), file = output)
                print(',', file=output)
        else:
            print(rec.PartialResult())

    with open(f'{audio_file[:-4]}_stt.txt', 'a') as output: 
        print (rec.FinalResult(), file = output)
        print (']', file = output)

    # СОХРАНЕНИЕ РЕЗУЛЬТАТА В ТЕКСТОВЫЙ ФАЙЛ
    # Мы перезаписываем тот же файл, в котором до этого делали предзапись результатов

    my_file = open (f'{audio_file[:-4]}_stt.txt', 'r') 
    content = my_file.read()
    print (type (content))
    res = json.loads (content)
    final_string = ''
    for i in res:
        final_string = ' '.join ((final_string, i['text']))
    print (final_string)

    with open(f'{audio_file[:-4]}_stt.txt', 'w') as output:  
        print (final_string, file = output)

    return final_string

path = f'C:\\Users\\User\\TikTok\\{nickname_stitch_needed}' # \\ чтобы \v не считывалось как символ

un_char_table = pd.read_csv (os.path.join (path, f'{nickname_stitch_needed}_unique_characteristics.csv'))
un_char_table = un_char_table.drop('Unnamed: 0', axis = 1).drop_duplicates ()

audio_path = os.path.join (path, 'audio_video')

for i in os.listdir (audio_path): 
    try:
        if i[-4:] == '.wav':
            aweme_index = un_char_table [un_char_table ['aweme_id'] == get_aweme_id_from_audio (i)].index
            print (f'aweme_id = {get_aweme_id_from_audio (i)}')
            un_char_table.at [aweme_index, 'stt_text'] = stt_function (os.path.join (audio_path, i)) # .at меняет значение в исходном датафрейме через индекс
            un_char_table.to_csv (os.path.join (path, f'{nickname_stitch_needed}_unique_characteristics.csv'))
    except:
        print (f'ОШИБКА aweme_index = {aweme_index}')
        pass

winsound.Beep (440, 1000)
