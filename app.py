from dotenv import load_dotenv
import os
import requests
import json
import time
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


@app.route('/', methods=['GET', 'POST'])
def index():
   print('Request for index page received')
   secret_nde = os.environ.get('SECRETNDE')
   print(secret_nde)
  
   ### appel crisp
   url = "https://api.crisp.chat/v1/website/5d62ac0f-8c10-4a47-9cb3-551838499efa/conversation/session_8cba96ad-ce3b-4e1f-b501-77faa9eaa2e9/message"

   payload = json.dumps({
   "type": "note",
   "from": "operator",
   "origin": "chat",
   "content": "test"
   })
   headers = {
   'Authorization': 'Basic {}'.format(CRISP_API),
   'Content-Type': 'application/json',
   'X-Crisp-Tier': 'plugin'
   }

   response = requests.request("POST", url, headers=headers, data=payload)

   print(response.text)
   

   ### azure transcribe
   if request.method == 'POST':
        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_recognition_language="fr-FR"

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        print("Speak into your microphone.")
        # Début de l'enregistrement vocal
        start_time = time.time()
        speech_recognition_result = speech_recognizer.recognize_once_async().get()
        # Fin de la reconnaissance vocale
        end_time = time.time()

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
            
            # Durée de la reconnaissance vocale en secondes
            duration = round(end_time - start_time, 2)
            print("Durée de la reconnaissance vocale: {} secondes".format(duration))

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



   return render_template('index.html', transcription='')


if __name__ == '__main__':
   app.run(debug=True)