import whisper
from faster_whisper import WhisperModel
from sst_app.config import logger, STATIC_PROMPT
import time
from collections import deque

openai_model = None
faster_model = None
previous_transcripts = deque(maxlen=3)

def load_whisper_model(model_type="openai"):
    global openai_model, faster_model
    logger.info(f"Loading Whisper model ({model_type})...")
    start_time = time.time()
    if model_type == "openai":
        openai_model = whisper.load_model("base")  # tiny, base, small, medium, large
    else:
        faster_model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=1)
    logger.info(f"Whisper model ({model_type}) loaded successfully in {time.time() - start_time:.2f} seconds.")

def generate_dynamic_prompt():
    previous_text = " ".join(previous_transcripts)
    return f"{STATIC_PROMPT}\n\nPrevious transcripts: {previous_text}"

def transcribe_audio(audio_data, language, model_type="openai"):
    global openai_model, faster_model, previous_transcripts
    if model_type == "openai" and openai_model is None:
        load_whisper_model("openai")
    elif model_type == "faster" and faster_model is None:
        load_whisper_model("faster")
    
    transcribe_start_time = time.time()
    dynamic_prompt = generate_dynamic_prompt()
    
    if model_type == "openai":
        result = openai_model.transcribe(audio_data, language=language, prompt=dynamic_prompt)
        transcription = result["text"].strip()
    else:
        segments, _ = faster_model.transcribe(audio_data, language=language, initial_prompt=dynamic_prompt)
        transcription = " ".join([segment.text for segment in segments]).strip()
    
    previous_transcripts.append(transcription)
    
    transcribe_duration = time.time() - transcribe_start_time
    logger.info(f"Transcription ({model_type}) completed in {transcribe_duration:.2f} seconds")
    logger.info(f"Transcription result: '{transcription}'")
    
    return transcription, transcribe_duration

def cleanup_whisper_models():
    global openai_model, faster_model
    if faster_model is not None:
        del faster_model
    if openai_model is not None:
        del openai_model
    openai_model = None
    faster_model = None
