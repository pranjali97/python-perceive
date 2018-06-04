"""Example of Python client calling Knowledge Graph Search API."""
import json
import vlc
import requests
from tkinter import *
from PIL import ImageTk, Image
from io import BytesIO
from google.cloud import texttospeech
import threading
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "//add_credentials"


# Call Google Knowledge Graph API

def synthesize_text(text):
    """Synthesizes speech from the input string of text."""
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.types.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')


def play_audio(filename='output.mp3'):
    p = vlc.MediaPlayer(filename)
    p.play()

def display_image(image_url, title):
    # Download the image

    n = 4

    r = requests.get(image_url)
    i = Image.open(BytesIO(r.content))
    imageSizeWidth, imageSizeHeight = i.size

    newImageSizeWidth = int(imageSizeWidth*n)
    newImageSizeHeight = int(imageSizeHeight*n)

    i = i.resize((newImageSizeWidth, newImageSizeHeight), Image.ANTIALIAS)

    # Draw the image using tkinter

    app_root = Tk()
    img = ImageTk.PhotoImage(i)
    imglabel = Label(app_root, image=img).grid(row=1, column=1)
    textlabel= Label(app_root, text=title).grid(row=2, column=1)
    app_root.mainloop()


def search(query):
    api_key = '//add_key'
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': query,
        'limit': 10,
        'indent': True,
        'key': api_key,
    }

    response = requests.get(service_url, params=params)

    # Extract Knowledge Graph data

    element = response.json()['itemListElement'][0]

    entity = element['result']['name']
    description = element['result']['detailedDescription']['articleBody'].strip()
    image_url = element['result']['image']['contentUrl']

    synthesize_text(description)
    play_audio()
    display_image(image_url, entity)
