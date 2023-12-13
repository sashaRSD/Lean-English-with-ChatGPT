from gtts import gTTS
import speech_recognition
#import pyttsx3
import os, time

sr = speech_recognition.Recognizer()
sr.pause_threshold = 0.5

# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# for voice in voices:
#     print('=======')
#     print('Имя: %s' % voice.name)
#     print('ID: %s' % voice.id)
#     print('Язык(и): %s' % voice.languages)
#     print('Пол: %s' % voice.gender)
#     print('Возраст: %s' % voice.age)


async def voice_to_text(file_dir, new_file_dir):
    os.system(f'ffmpeg -i {file_dir} {new_file_dir}')
    try:
        with speech_recognition.AudioFile(new_file_dir) as source:
            audio = sr.record(source=source)
            sr.adjust_for_ambient_noise(source=source, duration=0.5)
            voice_text = sr.recognize_google(audio_data=audio, language='en-US').lower()
    except speech_recognition.UnknownValueError:
        voice_text = 0
    time.sleep(1)
    os.remove(file_dir)
    os.remove(new_file_dir)
    return voice_text


async def text_to_voice(text, file_dir):
    tts = gTTS(text=text)
    tts.save(file_dir)
    # engine.setProperty('rate', 125)
    # engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
    # engine.setProperty("volume", 1)
    # engine.save_to_file(text, file_dir)
    # engine.runAndWait()
