from mycroft.skills.core import MycroftSkill, FallbackSkill, Message
from mtranslate import translate
import unicodedata
from langdetect import detect as language_detect


class AutotranslatableSkill(MycroftSkill):
    ''' Skill that auto translates speak messages '''

    def __init__(self, name=None, emitter=None):
        MycroftSkill.__init__(self, name, emitter)

    def language_detect(self, utterance):
        utterance = unicodedata.normalize('NFKD', unicode(utterance)).encode('ascii',
                                                                    'ignore')
        return language_detect(utterance)

    def translate(self, text, lang=None):
        lang = lang or self.lang
        sentence = translate(text, lang)
        translated = unicodedata.normalize('NFKD', unicode(
            sentence)).encode('ascii',
                                                                    'ignore')
        return translated

    def speak(self, utterance, expect_response=False,
              mute=False, more_speech=False, metadata=None,
              message_context=None):
        """
            Speak a sentence.

                   Args:
                       utterance:          sentence mycroft should speak
                       expect_response:    set to True if Mycroft should expect
                                           a response from the user and start
                                           listening for response.
                       mute:               ask to not execute TTS
                       more_speech:        signal more speak messages coming
                       metadata:           Extra data to be transmitted
                                           together with speech
                       message_context:    message.context field
               """
        # translate utterance for skills that generate speech at
        # runtime, or by request
        message_context = message_context or self.message_context
        utterance_lang = self.language_detect(utterance)
        if "-" in utterance_lang:
            utterance_lang = utterance_lang.split("-")[0]
        target_lang = self.lang
        if "-" in target_lang:
            target_lang = target_lang.split("-")[0]
        if utterance_lang != target_lang:
            utterance = self.translate(utterance, target_lang)
            message_context["auto_translated"] = True
            message_context["source_lang"] = utterance_lang
            message_context["target_lang"] = target_lang

        # registers the skill as being active
        self.enclosure.register(self.name)
        data = {'utterance': utterance,
                'expect_response': expect_response,
                "mute": mute,
                "more_speech": more_speech,
                "metadata": metadata}
        self.emitter.emit(Message("speak", data, self.get_message_context(
            message_context)))


class AutotranslatableFallback(FallbackSkill):
    ''' Fallback that auto translates speak messages and auto translates input '''

    def __init__(self, name=None, emitter=None):
        FallbackSkill.__init__(self, name, emitter)
        self.input_lang = None

    def language_detect(self, utterance):
        return language_detect(utterance)

    def translate(self, text, lang=None):
        lang = lang or self.lang
        sentence = translate(text, lang)
        translated = unicodedata.normalize('NFKD', sentence).encode('ascii',
                                                                    'ignore')
        return translated

    def speak(self, utterance, expect_response=False,
              mute=False, more_speech=False, metadata=None,
              message_context=None):
        """
            Speak a sentence.

                   Args:
                       utterance:          sentence mycroft should speak
                       expect_response:    set to True if Mycroft should expect
                                           a response from the user and start
                                           listening for response.
                       mute:               ask to not execute TTS
                       more_speech:        signal more speak messages coming
                       metadata:           Extra data to be transmitted
                                           together with speech
                       message_context:    message.context field
               """
        # translate utterance for skills that generate speech at
        # runtime, or by request
        message_context = message_context or self.message_context
        utterance_lang = language_detect(utterance)
        if "-" in utterance_lang:
            utterance_lang = utterance_lang.split("-")[0]
        target_lang = self.lang
        if "-" in target_lang:
            target_lang = target_lang.split("-")[0]
        if utterance_lang != target_lang:
            utterance = translate(utterance, target_lang)
            message_context["auto_translated"] = True
            message_context["source_lang"] = utterance_lang
            message_context["target_lang"] = target_lang

        # registers the skill as being active
        self.enclosure.register(self.name)
        data = {'utterance': utterance,
                'expect_response': expect_response,
                "mute": mute,
                "more_speech": more_speech,
                "metadata": metadata}
        self.emitter.emit(Message("speak", data, self.get_message_context(
            message_context)))

    def register_fallback(self, handler, priority):
        """
            register a fallback with the list of fallback handlers
            and with the list of handlers registered by this instance

            modify fallback handler for input auto-translation
        """
        if self.input_lang:
            def universal_translate_handler(message):
                # auto_Translate input
                ut = message.data.get("utterance")
                if ut:
                    ut_lang = self.language_detect(ut)
                    if "-" in ut_lang:
                        ut_lang = ut_lang.split("-")[0]
                    if "-" in self.input_lang:
                        self.input_lang = self.input_lang.split("-")[0]
                    if self.input_lang != ut_lang:
                        message.data["utterance"] = self.translate(ut,
                                                                   self.input_lang)
                success = handler(message)
                if success:
                    handler.__self__.make_active()
                return success

            self.instance_fallback_handlers.append(universal_translate_handler)
            skill_folder = self._dir  # skill
            if not skill_folder:
                raise EnvironmentError("could not get skill dir")
            self._register_fallback(universal_translate_handler, priority, skill_folder,
                                    self.handle_update_message_context)
        else:
            self.instance_fallback_handlers.append(handler)
            # folder path
            skill_folder = self._dir  # skill
            if not skill_folder:
                raise EnvironmentError("could not get skill dir")
            self._register_fallback(handler, priority, skill_folder,
                                    self.handle_update_message_context)
