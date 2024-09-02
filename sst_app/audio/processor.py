import numpy as np
import threading
import queue
import time
from sst_app.config import logger, SAMPLE_RATE, CHUNK_DURATION, AUDIO_DTYPE, OVERLAP_DURATION
from .utils import save_audio_segment
from sst_app.transcription.whisper_model import transcribe_audio
from sst_app.translation.translator import translate_text
from sst_app.utils.file_operations import save_transcript_and_translation
from datetime import datetime

audio_queue = queue.Queue()
translation_queue = queue.Queue()

def audio_processor(app):
    global previous_transcript
    previous_transcript = ""
    logger.info("Starting audio processor thread...")
    logger.info(f"USE_GPT4_TRANSLATION config value: {app.config.get('USE_GPT4_TRANSLATION', False)}")
    logger.info(f"USE_OVERLAPPING_CHUNKS config value: {app.config.get('USE_OVERLAPPING_CHUNKS', False)}")
    
    audio_buffer = np.array([], dtype=AUDIO_DTYPE)
    silence_threshold = 0.01
    last_process_time = time.time()
    new_session = True  # Add this flag

    while True:
        try:
            audio_chunk, input_lang, output_lang = audio_queue.get(timeout=1)
            
            if new_session:
                previous_transcript = ""
                new_session = False
            
            audio_buffer = np.concatenate((audio_buffer, audio_chunk))

            current_time = time.time()
            time_since_last_process = current_time - last_process_time
            logger.info(f"Current audio buffer length: {len(audio_buffer)}, Time since last process: {time_since_last_process:.2f}s")

            if len(audio_buffer) >= SAMPLE_RATE * CHUNK_DURATION and time_since_last_process >= CHUNK_DURATION:
                process_start_time = time.time()
                logger.info(f"Starting to process audio buffer of length: {len(audio_buffer)}")
                
                mean_amplitude = np.abs(audio_buffer).mean()
                logger.info(f"Mean amplitude: {mean_amplitude:.4f}")
                
                if mean_amplitude > silence_threshold:
                    logger.info("Audio level above silence threshold, transcribing...")
                    audio_buffer_contiguous = np.ascontiguousarray(audio_buffer, dtype=AUDIO_DTYPE)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_audio_segment(audio_buffer_contiguous, SAMPLE_RATE, input_lang, timestamp)
                    
                    transcription, transcribe_duration = transcribe_audio(audio_buffer_contiguous, input_lang)
                    
                    if transcription:
                        use_gpt4 = app.config['USE_GPT4_TRANSLATION']
                        logger.info(f"Using GPT-4 for translation: {use_gpt4}")  # Debug log
                        #combined_transcript = f"{previous_transcript}  {transcription}".strip()
                        combined_transcript = f"{transcription}".strip()
                        translation, translate_duration = translate_text(combined_transcript, src=input_lang, dest=output_lang, use_gpt4=use_gpt4)
                        result = {
                            "timestamp": timestamp,
                            "source_lang": input_lang,
                            "source_text": transcription,
                            "target_lang": output_lang,
                            "translated_text": translation
                        }
                        translation_queue.put(result)
                        save_transcript_and_translation(timestamp, input_lang, output_lang, transcription, translation)
                        logger.info(f"Translation result: {result}")
                        previous_transcript = transcription
                    else:
                        logger.info("No transcription produced for this audio chunk.")
                else:
                    logger.info(f"Detected silence, skipping processing.")

                # Preserve the last part of the buffer for the next chunk
                overlap_size = int(OVERLAP_DURATION * SAMPLE_RATE)
                audio_buffer = audio_buffer[-overlap_size:]
                last_process_time = current_time
                process_duration = time.time() - process_start_time
                logger.info(f"Total processing time for this chunk: {process_duration:.2f}s")

        except queue.Empty:
            logger.debug("No audio data received in the last second.")
            continue
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            logger.exception("Exception details:")
            translation_queue.put(f"Error: {str(e)}")

def start_audio_processor(app):
    logger.info(f"Starting audio processor with USE_GPT4_TRANSLATION = {app.config['USE_GPT4_TRANSLATION']}")
    audio_thread = threading.Thread(target=audio_processor, args=(app,))
    audio_thread.start()