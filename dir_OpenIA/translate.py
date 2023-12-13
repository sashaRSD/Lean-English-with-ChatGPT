from googletrans import Translator


async def translate_fun(text, src, to_lang):
    try:
        translator = Translator()
        translation = translator.translate(text=text, src=src, dest=to_lang)
        return translation.text
    except Exception as ex:
        return ''
