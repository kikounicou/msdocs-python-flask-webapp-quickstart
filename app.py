from dotenv import load_dotenv
import os
import requests
import json
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
app = Flask(__name__)

SPEECH_KEY = os.environ.get('SPEECH_KEY')
SPEECH_REGION = os.environ.get('SPEECH_REGION')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
CRISP_API = os.environ.get('CRISP_API')

# Liste pour stocker toutes les transcriptions précédentes
transcriptions = []

def configure():
    load_dotenv()


@app.route('/')
def index():
   print('Request for index page received')
   secret_nde = os.environ.get('SECRETNDE')
   print(secret_nde)
  
   ### appel crisp
   url = "https://api.crisp.chat/v1/website/5d62ac0f-8c10-4a47-9cb3-551838499efa/conversation/session_70c3b308-9a18-439e-87f1-961726cf9100/"
   payload={}
   headers = {
    'Authorization': 'Basic {}'.format(CRISP_API),
    'X-Crisp-Tier': 'plugin'
    }
   response = requests.request("GET", url, headers=headers, data=payload)
   print(response.text)

   ### azure transcribe
   if request.method == 'POST':
        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_recognition_language="fr-FR"

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        print("Speak into your microphone.")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
            # Ajouter la nouvelle transcription à la liste des transcriptions
            transcriptions.append(speech_recognition_result.text)
            # Concaténer toutes les transcriptions en une seule chaîne de caractères
            transcription = '\n'.join(transcriptions)
            
            # Build JSON payload
            payload = {
                "text": transcription
            }
            # Send POST request to webhook endpoint with JSON payload
            response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
            print("Webhook response: {}".format(response.status_code))
            
            # ajoute la transcription dans le textarea
            return render_template('index.html', transcription=transcription)

        
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
   else:
        # Si la requête est GET, réinitialiser la liste des transcriptions et la variable transcription
        transcriptions.clear()
        transcription = ''



   return render_template('index.html', secret_nde=secret_nde)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   configure()
   name = request.form.get('name')
   print("hello")
   secret_nde = os.environ.get('SECRETNDE')
   print(secret_nde)

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name, secret_nde=secret_nde)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run(debug=True)