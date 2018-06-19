import time

from mycroft.util import play_wav
from mycroft.util.log import LOG
from mycroft.tts import TTS, TTSValidator
from mycroft.configuration import Configuration
from mycroft import MYCROFT_ROOT_PATH

__author__ = 'jarbas'


class BeepSpeak(TTS):
    def __init__(self, lang="en-us", voice="r2d2", timestep=0.3):
        super(BeepSpeak, self).__init__(lang, voice, BeepSpeakValidator(self))
        config = Configuration.get().get("tts").get("beep_speak", {})
        self.time_step = float(config.get("time_step", timestep))
        self.voice = config.get("voice", voice)
        self.lang = config.get("lang", lang)
        self.sound_files_path = config.get("sounds", MYCROFT_ROOT_PATH +
                                           "/mycroft/res/beep_speak_sound_files")

        self.process = None
        # support these chars
        self.code = ["?", "!", ".", "+", "-", "*", "A", "B", "C", "D", "E",
                     "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
                     "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "1",
                     "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    def verify(self, string):
        for char in string:
            if char.upper() not in self.code and char != ' ':
                LOG.warn('Error the character ' + char + ' cannot be ' \
                                                         'translated to ' \
                                                         'beep_speak')
                string.replace(char.upper(), "").replace(char, "")

    def execute(self, msg):

        self.verify(msg)

        for char in msg:
            if char == ' ':
                time.sleep(2 * self.time_step)
            else:
                morse_sound_path = self.sound_files_path + "/" + \
                                   char.upper() + '_beep.wav'
                self.process = play_wav(morse_sound_path)
                time.sleep(self.time_step)  # ~sound duration


class BeepSpeakValidator(TTSValidator):
    def __init__(self, tts):
        super(BeepSpeakValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO
        pass

    def validate_connection(self):
        # TODO check if sound files exist
        pass

    def get_tts_class(self):
        return BeepSpeak
