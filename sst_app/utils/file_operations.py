import os
import json
from sst_app.config import logger

def save_transcript_and_translation(timestamp, input_lang, output_lang, transcription, translation):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    filename = f"data/transcript_{timestamp}_{input_lang}_{output_lang}.txt"
    
    data = {
        "timestamp": timestamp,
        "input_language": input_lang,
        "output_language": output_lang,
        "transcription": transcription,
        "translation": translation
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved transcript and translation: {filename}")
