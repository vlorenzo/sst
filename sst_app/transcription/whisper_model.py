import whisper
from sst_app.config import logger, STATIC_PROMPT
import time
from collections import deque

model = None
previous_transcripts = deque(maxlen=3)

def load_whisper_model():
    global model
    logger.info("Loading Whisper model...")
    start_time = time.time()
    model = whisper.load_model("small")
    logger.info(f"Whisper model loaded successfully in {time.time() - start_time:.2f} seconds.")

def generate_dynamic_prompt():
    previous_text = " ".join(previous_transcripts)
    return f"{STATIC_PROMPT}\n\nPrevious transcripts: {previous_text}"

def transcribe_audio(audio_data, language):
    global model, previous_transcripts
    if model is None:
        load_whisper_model()
    
    transcribe_start_time = time.time()
    dynamic_prompt = generate_dynamic_prompt()
    result = model.transcribe(audio_data, language=language, prompt=dynamic_prompt)
    
    transcription = result["text"].strip()
    previous_transcripts.append(transcription)
    
    transcribe_duration = time.time() - transcribe_start_time
    logger.info(f"Transcription completed in {transcribe_duration:.2f} seconds")
    logger.info(f"Transcription result: '{transcription}'")
    
    return transcription, transcribe_duration
