from pygoogletranslation import Translator
from urllib.parse import quote
import requests
from sst_app.config import logger
import time
from openai import OpenAI
import os

translator = Translator()

# Read OpenAI API key from environment variable
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def translate_text(text, src='it', dest='en', use_gpt4=False):
    logger.info(f"Translate function called with use_gpt4={use_gpt4}")  # Debug log
    if use_gpt4:
        return translate_text_gpt4(text, src, dest)
    else:
        return translate_text_google(text, src, dest)

def translate_text_google(text, src='it', dest='en'):
    start_time = time.time()
    try:
        translation = translator.translate(text, src=src, dest=dest).text
        duration = time.time() - start_time
        logger.info(f"Google translation completed in {duration:.2f} seconds")
        return translation, duration
    except Exception as e:
        logger.warning(f"Pygoogletrans translation failed: {str(e)}")

        try:
            encoded_text = quote(text)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src}&tl={dest}&dt=t&q={encoded_text}"
            response = requests.get(url)
            if response.status_code == 200:
                translation = response.json()[0][0][0]
                duration = time.time() - start_time
                logger.info(f"Fallback Google translation completed in {duration:.2f} seconds")
                return translation, duration
            else:
                logger.error(f"Fallback Google translation failed with status code: {response.status_code}")
                return f"Translation error: HTTP {response.status_code}", time.time() - start_time
        except Exception as e:
            logger.error(f"Fallback Google translation failed: {str(e)}")
            return f"Translation error: {str(e)}", time.time() - start_time

def translate_text_gpt4(text, src='it', dest='en'):
    start_time = time.time()
    try:
        system_prompt = f"""
        You are a professional translator. Translate the users text from {src} to {dest}.
        Correct any errors if present, considering the following names and context: You are translating a live talk at an event in Bologna hosted by Versya, Lorenzo Verna is the  CTO at Twiper.
        Maintain the original meaning and tone of the text while providing an accurate and natural translation.
        Just return the translation, no intro, no explanation, no commentary.
        """

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )

        translation = response.choices[0].message.content.strip()
        duration = time.time() - start_time
        logger.info(f"GPT-4 translation completed in {duration:.2f} seconds")
        return translation, duration
    except Exception as e:
        logger.error(f"GPT-4 translation failed: {str(e)}")
        return f"Translation error: {str(e)}", time.time() - start_time
    