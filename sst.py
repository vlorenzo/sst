from flask import Flask, render_template, request, jsonify
import whisper
from googletrans import Translator
from urllib.parse import quote
import numpy as np
import threading
import queue
import time
import logging
import requests
import argparse
import os
import wave
from datetime import datetime
import soundfile as sf
from collections import deque
import json


# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_app(input_lang='it', output_lang='en'):
    app = Flask(__name__)
    app.config['INPUT_LANG'] = input_lang
    app.config['OUTPUT_LANG'] = output_lang

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload_audio', methods=['POST'])
    def upload_audio():
        logger.info("Received audio upload request")
        if request.data:
            try:
                start_time = time.time()
                audio, process_duration = process_audio(request.data)
                audio_queue.put(audio)
                total_duration = time.time() - start_time
                logger.info(f"Audio upload and initial processing completed in {total_duration:.2f} seconds")
                return jsonify({
                    'message': 'Audio received and processing',
                    'audio_process_time': process_duration,
                    'total_upload_time': total_duration
                }), 200
            except Exception as e:
                logger.error(f"Error processing uploaded audio: {str(e)}")
                return jsonify({'error': str(e)}), 500
        return jsonify({'error': 'No audio data received'}), 400

    @app.route('/get_translation')
    def get_translation():
        logger.info("Received translation request")
        global translation_result
        if translation_result:
            result = translation_result
            translation_result = None
            return jsonify({'translation': result})
        return jsonify({'translation': None})

    return app



# Load Whisper model
logger.info("Loading Whisper model...")
start_time = time.time()
model = whisper.load_model("small")
logger.info(f"Whisper model loaded successfully in {time.time() - start_time:.2f} seconds.")

# Initialize translator
logger.info("Initializing Translator...")
start_time = time.time()
translator = Translator()
logger.info(f"Translator initialized successfully in {time.time() - start_time:.2f} seconds.")

# Audio processing settings
SAMPLE_RATE = 16000  # Whisper expects 16kHz audio
CHUNK_DURATION = 3  # Process 3 seconds of audio at a time
AUDIO_DTYPE = np.float32

audio_queue = queue.Queue()
translation_result = None

# global variables for dynamic prompt   
static_prompt = """
Nomi: Lorenzo, Lorenzo Verna, Twiper, AGER, Bologna.
Acronimi: CTO (Chief Technology Officer)
Termini Tecnici: AGER, Evento AGER, Artificial Intelligence, SST (Simultaneous Speech Translator).
Frase di saluto: Buongiorno a tutti, sono Lorenzo Verna, CTO di Twiper. Benvenuti al Evento AGER. E' un piacere condividere con voi. le nostre soluzioni di Intelligenza Artificale applicate al vostro business. 
"""
previous_transcripts = deque(maxlen=3)  # Store the last 3 transcripts


def translate_text(text, src='it', dest='en'):
    start_time = time.time()
    try:
        # First attempt: Use googletrans
        translation = translator.translate(text, src=src, dest=dest).text
        duration = time.time() - start_time
        logger.info(f"Translation completed in {duration:.2f} seconds")
        return translation, duration
    except Exception as e:
        logger.warning(f"Googletrans translation failed: {str(e)}")

        # Fallback: Use direct HTTP request to Google Translate
        try:
            encoded_text = quote(text)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src}&tl={dest}&dt=t&q={encoded_text}"
            response = requests.get(url)
            if response.status_code == 200:
                translation = response.json()[0][0][0]
                duration = time.time() - start_time
                logger.info(f"Fallback translation completed in {duration:.2f} seconds")
                return translation, duration
            else:
                logger.error(f"Fallback translation failed with status code: {response.status_code}")
                return f"Translation error: HTTP {response.status_code}", time.time() - start_time
        except Exception as e:
            logger.error(f"Fallback translation failed: {str(e)}")
            return f"Translation error: {str(e)}", time.time() - start_time

def process_audio(audio_data):
    start_time = time.time()
    audio_array = np.frombuffer(audio_data, dtype=AUDIO_DTYPE)

    # Ensure the audio is at the correct sample rate
    if len(audio_array) > 0:
        input_sample_rate = len(audio_array) / CHUNK_DURATION
        if input_sample_rate != SAMPLE_RATE:
            resampled = np.interp(
                np.linspace(0, CHUNK_DURATION, int(CHUNK_DURATION * SAMPLE_RATE), dtype=AUDIO_DTYPE),
                np.linspace(0, CHUNK_DURATION, len(audio_array), dtype=AUDIO_DTYPE),
                audio_array
            ).astype(AUDIO_DTYPE)
            duration = time.time() - start_time
            logger.info(f"Audio processing (with resampling) completed in {duration:.2f} seconds")
            return resampled, duration
        else:
            duration = time.time() - start_time
            logger.info(f"Audio processing (no resampling) completed in {duration:.2f} seconds")
            return audio_array, duration

    logger.warning("Received empty or invalid audio data")
    return np.array([], dtype=AUDIO_DTYPE), time.time() - start_time


# Add this function to save audio segments

def save_audio_segment(audio_data, sample_rate, input_lang, timestamp):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    filename = f"data/audio_{timestamp}_{input_lang}.wav"
    
    # Debug information
    logger.debug(f"Original audio data - min: {np.min(audio_data)}, max: {np.max(audio_data)}, dtype: {audio_data.dtype}")
    
    # Ensure audio data is in float32 format
    audio_float = audio_data.astype(np.float32)
    
    # Normalize audio to range [-1, 1]
    audio_normalized = audio_float / np.max(np.abs(audio_float))
    
    # Apply a gain to make it more audible (adjust as needed)
    gain = 0.5
    audio_amplified = audio_normalized * gain
    
    # Clip to ensure no values exceed [-1, 1]
    audio_clipped = np.clip(audio_amplified, -1, 1)
    
    # Debug information after processing
    logger.debug(f"Processed audio data - min: {np.min(audio_clipped)}, max: {np.max(audio_clipped)}")
    
    # Save using soundfile library
    sf.write(filename, audio_clipped, sample_rate)
    
    logger.info(f"Saved audio segment: {filename}")


def generate_dynamic_prompt(static_prompt, previous_transcripts):
    previous_text = " ".join(previous_transcripts)
    logger.debug(f"Dynamic prompt: {static_prompt}\n\nPrevious transcripts: {previous_text}")
    return f"{static_prompt}\n\nPrevious transcripts: {previous_text}"

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


def audio_processor(app):
    logger.info("Starting audio processor thread...")
    global translation_result
    audio_buffer = np.array([], dtype=AUDIO_DTYPE)
    silence_threshold = 0.01
    last_process_time = time.time()

    while True:
        try:
            audio_chunk = audio_queue.get(timeout=1)
            audio_buffer = np.concatenate((audio_buffer, audio_chunk))

            current_time = time.time()
            time_since_last_process = current_time - last_process_time
            logger.info(f"Current audio buffer length: {len(audio_buffer)}, Time since last process: {time_since_last_process:.2f}s")

            if len(audio_buffer) >= SAMPLE_RATE * CHUNK_DURATION and time_since_last_process >= CHUNK_DURATION:
                process_start_time = time.time()
                logger.info(f"Starting to process audio buffer of length: {len(audio_buffer)}")
                
                # Check for silence
                mean_amplitude = np.abs(audio_buffer).mean()
                logger.info(f"Mean amplitude: {mean_amplitude:.4f}")
                
                if mean_amplitude > silence_threshold:
                    logger.info("Audio level above silence threshold, transcribing...")
                    audio_buffer_contiguous = np.ascontiguousarray(audio_buffer, dtype=AUDIO_DTYPE)
                    
                    # Log some debug information
                    logger.debug(f"Audio buffer shape: {audio_buffer_contiguous.shape}")
                    logger.debug(f"Audio buffer dtype: {audio_buffer_contiguous.dtype}")
                    logger.debug(f"Audio buffer min: {np.min(audio_buffer_contiguous)}, max: {np.max(audio_buffer_contiguous)}")
                    
                   # Save the audio segment
                    input_lang = app.config['INPUT_LANG']
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_audio_segment(audio_buffer_contiguous, SAMPLE_RATE, input_lang, timestamp)
                    
                    
                    # Transcription
                    transcribe_start_time = time.time()
                    dynamic_prompt = generate_dynamic_prompt(static_prompt, previous_transcripts)
                    result = model.transcribe(audio_buffer_contiguous, 
                                              language=input_lang, 
                                              prompt=dynamic_prompt)
                    #result = model.transcribe(audio_buffer_contiguous, language=input_lang)
                
                    transcribe_duration = time.time() - transcribe_start_time
                    logger.info(f"Transcription completed in {transcribe_duration:.2f} seconds")
                    
                    transcription = result["text"].strip()
                    logger.info(f"Transcription result: '{transcription}'")

                    previous_transcripts.append(transcription)

                    if transcription:
                        # Translation
                        output_lang = app.config['OUTPUT_LANG']
                        translation, translate_duration = translate_text(transcription, src=input_lang, dest=output_lang)
                        #translation, translate_duration = translate_text(transcription, src='it', dest='en')
                        logger.info(f"Translation completed in {translate_duration:.2f} seconds")
                        translation_result = translation
                        logger.info(f"{input_lang.capitalize()} Transcription: {transcription}")
                        logger.info(f"{output_lang.capitalize()} Translation: {translation}")
                        # Save transcript and translation
                        save_transcript_and_translation(timestamp, input_lang, output_lang, transcription, translation)
                    
                    else:
                        logger.info("No transcription produced for this audio chunk.")
                else:
                    logger.info(f"Detected silence, skipping processing.")

                audio_buffer = np.array([], dtype=AUDIO_DTYPE)
                last_process_time = current_time
                process_duration = time.time() - process_start_time
                logger.info(f"Total processing time for this chunk: {process_duration:.2f}s")
                
                # Log a summary of timings for this chunk
                logger.info("Timing summary for this chunk:")
                logger.info(f"  Audio processing: {time_since_last_process:.2f}s")
                if mean_amplitude > silence_threshold:
                    logger.info(f"  Transcription: {transcribe_duration:.2f}s")
                    if transcription:
                        logger.info(f"  Translation: {translate_duration:.2f}s")
                logger.info(f"  Total processing: {process_duration:.2f}s")
            else:
                logger.debug("Not enough audio data accumulated yet for processing.")
        except queue.Empty:
            logger.debug("No audio data received in the last second.")
            continue
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            logger.exception("Exception details:")
            translation_result = f"Error: {str(e)}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Speech-to-Text and Translation App')
    parser.add_argument('--input_lang', default='it', help='Input language code (default: it)')
    parser.add_argument('--output_lang', default='en', help='Output language code (default: en)')
    args = parser.parse_args()

    app = create_app(input_lang=args.input_lang, output_lang=args.output_lang)
    logger.info(f"Starting app with input language: {app.config['INPUT_LANG']} and output language: {app.config['OUTPUT_LANG']}")
    
    # Start the audio processor thread
    audio_thread = threading.Thread(target=audio_processor, args=(app,))
    audio_thread.start()
    
    app.run(debug=True, use_reloader=False)
