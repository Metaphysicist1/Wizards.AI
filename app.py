
from flask import Flask, request, jsonify # for app defining, tracking and returning.

from werkzeug.utils import secure_filename # for audio name validating.

import speech_recognition as sr # for using speech2text pocketSphinx module.

import logging # for log working / describing.

import time # for audio transcribing time identifing.

import psutil # for cpu,ram,disk value counting.

import threading # for threads counting.

import os #for path accessing.

from scipy.io import wavfile # for getting audio duration.



from vosk import Model, KaldiRecognizer
import sys
import json #?
import wave




logging.basicConfig(filename = 'logs.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')



app = Flask(__name__)   # переменная приложения

@app.errorhandler(400)
def Bad_Request(e):
    app.logger.info('Client Error 400 Bad Request')
    return jsonify({
                    'text':'HTTP Client Error Bad Request',
                    'Response Code':400,
                    }) 




@app.errorhandler(403)
def page_forbidden(e):
    app.logger.info('Client Error 403 Forbidden')
    return jsonify({
                    'text':'HTTP Client Error Forbidden',
                    'Response Code':403,
                    }) 

@app.errorhandler(404)
def page_not_found(e):
    app.logger.info('Client Error 404 Not Found')
    return jsonify({
                    'text':'HTTP Client Error Not Found',
                    'Response Code':404,
                    }) 

@app.errorhandler(405)
def MethodNotAllowed(e):
    app.logger.info('Response code 405 Method Not Allowed')
    return jsonify({
                    'text':'HTTP Error Method Not Allowed',
                    'Response Code':405,
                    }) 





def file_verify(file): # проверка деиствительности имени файла.
    try:

        # аргументом функций должно быть имя файла.

        ALLOWED_EXTENSIONS = {'wav','mp3','ogg'}   # допустимые форматы аудио фаила

        file.filename = secure_filename(file.filename)

        
        return file.filename != '' and file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS # возврашает True/False
    except:
        app.logger.error('|Error with file validating')


def Vosk_Kaldi_detection(filename):

    detected_text=[]

    if not os.path.exists("model"):
        print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit (1)

    wf = wave.open(filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print ("Audio file must be WAV format mono PCM.")
        exit (1)

    model = Model("model")

    # You can also specify the possible word or phrase list as JSON list, the order doesn't have to be strict
    rec = KaldiRecognizer(model, wf.getframerate(), '["oh one two three four five six seven eight nine zero", "[unk]"]')

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            detected_text.append(rec.Result())

    return detected_text



def Sphinx_detection(filename):    # функция распознания речи принимает аргумент имя файла

    try:

        r = sr.Recognizer() # инициализация обьекта для распознания речию

        with sr.AudioFile(filename) as source: # использовать аудио файл как аудио поток

            audio = r.record(source)    # чтения аудио потока

            app.logger.info('|Text Recognition Finished successfully')    

            return r.recognize_sphinx(audio)   # возврашения обработоного аудио сигнала  

    except:
        app.logger.error('|Error with audio reognition.')
 

def Vosk_detection(filename):
    
    model = Model("model")

    # Large vocabulary free form recognition
    rec = KaldiRecognizer(model, 16000)
    
    # You can also specify the possible word list
    #rec = KaldiRecognizer(model, 16000, "zero oh one two three four five six seven eight nine")
    
    wf = open(filename, "rb")
    
    
    while True:
        data = wf.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            print (res['text'])

    res = json.loads(rec.FinalResult())
    return res
 

@app.route('/', methods=['GET','POST'])   # соединаем наш адресс и  функцию деиствия с помошью методов.

def upload_file():  # функция запукает метод POST для принятия данных (аудиофайл) и метод GET для отправки загрузочной формы а также для отправки JSON ответа (распознанный текст).

    

    try:    # проверка на ошибки

        if request.method == 'POST':  # метод комуникаций  

            file = request.files['file'] # локальная переменная в которой сохраняем принятый файл.

            app.logger.info('|Getting file finished successfully')   

            if file_verify(file):    # проверка присуствие файла, проверка его имени и допустимость формата.

                # дополнительная проверка имени файла 
                
                app.logger.info('|File Name Verified successfully')

                file.save(file.filename)

                file_path = os.path.abspath(os.getcwd())+'/'+file.filename

                file_size = os.path.getsize(file_path)/1000    

                
                Fs, data = wavfile.read(file.filename)
                n = data.size
                audio_length = n / Fs  
                
                # = AudioSegment.from_file(file_path).duration_seconds 

                app.logger.info('|Audio file saved successfully')

                cpu_val = psutil.cpu_percent()

                ram_val = psutil.virtual_memory().percent

                free_space = psutil.disk_usage("/").free / (2**30)

                start_time =  time.time() #for counting

                start_str =  time.strftime("%H:%M:%S", time.localtime()) # for log printing

                Sphinx_recognition = Sphinx_detection(file.filename)

                Vosk_recognition = Vosk_detection(file.filename)

                Vosk_Kaldi_recognition = Vosk_Kaldi_detection(file.filename)
              
                finish_time =  time.time()  #for counting        
       
                spent_time = finish_time-start_time                

                finish_str =  time.strftime("%H:%M:%S", time.localtime())  # for log printing

 

                app.logger.info("#audio_length (sec): "+str(audio_length))
                app.logger.info("#filename: "+str(file.filename))
                app.logger.info("#file_size (kb): " + str(file_size))

                app.logger.info('%' + 'Start: '+str(start_str) )

                app.logger.info('%' + 'Finish: '+str(finish_str))

                app.logger.info('%' + 'spent: '+str(round(spent_time,2)) )

                

                app.logger.info('%CPU USAGE: '+str(cpu_val)+"%" )

                app.logger.info('%RAM USAGE: '+str(ram_val)+"%" )

                app.logger.info('%'+'Free Space: '+str(round(free_space,1)))

                app.logger.info('%'+'Active Threadings: '+str(threading.active_count()))

               

                return jsonify({   # возврашаем имя аудио фаила и распознаный текст с аудио примера.

                    "Finish":finish_str,
                    
                    "Start":start_str,

                    "spent_time":spent_time,

                    "error_level":0,

                    "Audio_File_Name":file.filename,

                    "Audio_Length (sec)":audio_length,

                    "file_size (kb)" :file_size,

                    "Sphinx Result":Sphinx_recognition,
                    "Vosk Result":Vosk_recognition,
                    "Vosk_Kaldi Result":Vosk_Kaldi_recognition
                    })

 

            else:  # при ошибке в имени файла активируем ответ

                app.logger.error('|Maybe you did not upload file or have upload file with incorrect file type or name.Try Again') 
                raise Exception()

           

            

 

    except:   # при других сторонних ошибках  возврашаем ответ

        

        return jsonify('There is error regarding libraries or other'),app.logger.info('Raised Exception')

              

            # возврашаем форму для загрузки файла и отправки через API

    return '''

    <!doctype html>

    <title>Upload new File</title>

    <h1>Upload new File</h1>

    <form method=post enctype=multipart/form-data>

      <input type=file name=file>

      <input type=submit value=Upload>

    </form>

    '''

 

 

 

if __name__=="__main__":

  app.run(host='localhost',debug=True) # загрузка данного приложения