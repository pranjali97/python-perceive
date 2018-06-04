import speech_recognition as sr
import subprocess
from subprocess import call
import os
import gnk
import time
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "//add_credentials"

def prepare_date(self):
    self.response = self.response + self.result[2:18]

def prepare_time(self):
    self.response = self.response + self.result[2:-2]

class Action(object):
    def __init__(self, command, response, preparator=None):
        super(Action, self).__init__()
        self.command = command
        self.response = response
        self.result = None
        if preparator:
            self.prepare_response = preparator
        else:
            self.prepare_response = lambda: None

    def execute(self):
        self.result = str(subprocess.check_output(self.command))

    def respond(self):
        self.prepare_response(self)
        print(self.response)
        gnk.synthesize_text(self.response)
        gnk.play_audio()

r = sr.Recognizer()
m = sr.Microphone()
action_mapper = dict()

action_mapper['increase brightness'] = Action('xbacklight -inc 40 && xbacklight',
                                              'I have increased the brightness by 40%')
action_mapper['current user'] = Action('whoami', '')
action_mapper['decrease brightness'] = Action('xbacklight -dec 40 && xbacklight',
                                              'I have decreased the brightness by 40%')
action_mapper['date'] = Action(['date', '-R'], 'The date is ', prepare_date)
action_mapper['time'] = Action(['date', '+%r'], 'The time is ', prepare_time)
action_mapper['disk usage'] = Action('du', 'View the terminal')
action_mapper['current session information'] = Action('w', 'View the terminal for the current session info')
action_mapper['free disk space'] = Action('df', 'free disk space dsiplayed on the terminal')
action_mapper['editor'] = Action('gedit', 'i have opened the editor')

try:
    print("A moment of silence, please...")
    with m as source:
        r.adjust_for_ambient_noise(source)
    print("Set minimum energy threshold to {}".format(r.energy_threshold))
    while True:
        print("Say something!")
        with m as source:
            audio = r.listen(source)
        print("Got it! Trying to recognize...")
        try:
            # speech to text
            value = r.recognize_google_cloud(audio)
            print("You said {}".format(value))
            action_obj = action_mapper[value.strip()]
            action_obj.execute()
            action_obj.respond()

        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except KeyError:
            try:
                gnk.play_audio("google_lookup.mp3")
                player = gnk.search(value.strip())
            except (IndexError, KeyError):
                gnk.play_audio("no_results.mp3")
        except sr.RequestError as e:
            print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
        time.sleep(13)
except KeyboardInterrupt:
    pass
