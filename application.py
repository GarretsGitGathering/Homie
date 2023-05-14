# CSP final project
# By Garret Washburn & Ryan Stenz

# FFmpeg binaries are included

from __future__ import unicode_literals

# import modules for speech-to-text and text-to-speech
import azure.cognitiveservices.speech as speechsdk
import time
from flashtext import KeywordProcessor

# import modules for time
from datetime import datetime

# import modules for weather
import requests
import json
import math

# import modules for youtube function
import simpleaudio as sa
import youtube_dl
import urllib.request
from bs4 import BeautifulSoup

# keyword processor to look for *key words*
keyword_processor = KeywordProcessor()
keyword_processor.add_keyword("play")
keyword_processor.add_keyword("don't")
keyword_processor.add_keyword("do not")
keyword_processor.add_keyword("say")
keyword_processor.add_keyword("weather")
keyword_processor.add_keyword("kazoo")
keyword_processor.add_keyword("how are you")
keyword_processor.add_keyword("grade")
keyword_processor.add_keyword("I love you")
keyword_processor.add_keyword("stop listening")
keyword_processor.add_keyword("time")
keyword_processor.add_keyword("date")

# openweathermap stuff
weather_api_key = "*api_key_string"

# base_url variable to store url
base_url = "http://api.openweathermap.org/data/2.5/weather?"

# city name
city_name = "city_name"

# complete url address
complete_url = base_url + "appid=" + weather_api_key + "&q=" + city_name

response = requests.get(complete_url)

# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and region identifier from here: https://aka.ms/speech/sdkregion
speech_key, service_region = "*api_key_string", "region"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Creates a recognizer with the given settings
#speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input) # use file
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config) # use microphone

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config) # text to speech

print("Listening")

done = False

# stops recognition function
def stop_cb(evt):
    """callback that signals to stop continuous recognition upon receiving an event `evt`"""
    #print('CLOSING on {}'.format(evt))
    done = True

#### HANDLE KEYWORDS ###
def handleKeyword(keyword, text):
    if text != "":
        print("Handling keyword", keyword, "using", text)
    else:
        print("Handling keyword", keyword)
    
    ### CALLS ON YOUTUBE FUNCTION ###
    if keyword == "play":
        if text != "":
            print("Searching for", text)
            say("Searching for " + text)
            playYouTube(text)
        else:
            print("You can't search for an empty string you dummy!!!")
            say("You can't search for an empty string you dummy!!!")
    if keyword == "don't" or keyword == "do not":
        print("Okay, I won't", text)
        say("Okay, I won't " + text)
    if keyword == "say":
        say(text)
    if keyword == "grade":
        say("Ryan and Garret get an A+ on this project because it's very awesome and very epic")
    if keyword == "stop listening":
        say("Okay")
        speech_recognizer.stop_continuous_recognition()
        print("\nNot listening")
        input("Press Enter to start listening")
        speech_recognizer.start_continuous_recognition()
    if keyword == "time": # tells the time
        now = datetime.now()
        hour = now.strftime("%I")
        minute = now.strftime("%M")
        ampm = now.strftime("%p")
        print("It's", str(hour) + ":" + str(minute), str(ampm))
        say("It's " + str(hour) + " " + str(minute) + " " + str(ampm))
    if keyword == "date": # tells the date
        today = datetime.today()
        date_format = today.strftime("%B %d, %Y")
        print("It's", date_format)
        say("It's " + str(date_format))
    
    ### THE WEATHER FUNCTION ###
    if keyword == "weather":
        print("Getting data")
        weather_data = response.json()
        print("Got data")
        if weather_data["cod"] != "404":
            # organizing the different weather aspects
            temp = weather_data["main"]
            current_temperature = temp["temp"]
            current_humidiy = temp["humidity"]

            # the printing and saying of the different weather aspects
            temp_in_f = (((current_temperature - 273.15) * 1.8) + 32) # convert kelvin to fahrenheit
            temp_in_f = int(round(temp_in_f))
            print("The current temperature in", city_name, "is", str(temp_in_f), "degrees fahrenheit")
            print("The current humidity is", str(current_humidiy), "percent")

            say("The current temperature in " + city_name + " is " + str(temp_in_f) + \
                "degrees fahrenheit, and the current humidity is " + str(current_humidiy) + " percent")
            if current_humidiy >= 90:
                say("It's probably going to rain, make sure you bring an umbrella!")
        else:
            print("404 error while getting the current weather")
            say("404 error while getting the current weather")
    
    ### SAYS RANDOM FUNNY THINGS WE WANT IT TO ###
    if keyword == "kazoo":
        say("You should probably turn down your volume lol")
        say("Like actually, you really need to turn your volume down a lot")
        playYouTubeUrl("https://www.youtube.com/watch?v=up1l0n3qBYs")
        say("I warned you!!")
    if keyword == "how are you":
        playYouTubeUrl("https://www.youtube.com/watch?v=77sS5IuR0Gs")

### YOUTUBE SEARCH PART OF CODE ###
# the configuration for youtube_dl
options = {
    'format': 'bestaudio/best',
    'audio-format': 'wav',
    'outtmpl': 'audio.%(ext)s',
    'no-playlist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }],
}

def playYouTube(search): # plays the youtube video with search data after being called
    query = urllib.parse.quote(search)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        if not vid['href'].startswith("https://googleads.g.doubleclick.net/"):
            url = 'https://www.youtube.com' + vid['href']
            print(url)
            break # break out of the loop, i didn't know how to just get one url in a way that would work, so yeah this isn't really a loop anymore

    # download the video as a wav file
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([url])

    # plays audio file
    filename = 'audio.wav'
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # wait until sound has finished playing

def playYouTubeUrl(url): # just plays youtube videos with a given url
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([url])

    # plays audio file
    filename = 'audio.wav'
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done() # wait until sound has finished playing

### THE ACTUAL VOICE RECOGNITION ###
def recognized(evt):
    text = ('{}'.format(evt.result.text))
    speech_recognizer.stop_continuous_recognition()
    print("\n", text, "\n")

    keyword_list = keyword_processor.extract_keywords(text)

    if len(keyword_list) >= 1:
        print("Keywords:", keyword_list)
        print("Using keyword", keyword_list[0]) # the keyword will always be the first one recognized

        text_lower = text.lower() # the string must all be lower case, in order to be matched with the keywords
        idx = text_lower.find(keyword_list[0])
        text_after_keyword = text_lower[(1+idx+(len(keyword_list[0]))):] # identifies the words after the keyword
        print(text_after_keyword)

        handleKeyword(str(keyword_list[0]),text_after_keyword) # handle the keyword (only the first keyword it heard!!!!!!!)

    speech_recognizer.start_continuous_recognition()
    print("Listening")

def say(text):
    speech_synthesizer.speak_text_async(text)

speech_recognizer.recognized.connect(recognized)
speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(stop_cb)

### START CONTINUOUS SPEECH RECOGNITION ###
speech_recognizer.start_continuous_recognition()
while not done:
    time.sleep(.5)

speech_recognizer.stop_continuous_recognition()
