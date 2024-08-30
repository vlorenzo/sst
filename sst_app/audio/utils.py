from sst_app.config import logger, SAMPLE_RATE, CHUNK_DURATION, AUDIO_DTYPE
import numpy as np
import soundfile as sf
import os
import time

def process_audio(audio_data):
    start_time = time.time()
    audio_array = np.frombuffer(audio_data, dtype=AUDIO_DTYPE)

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

def save_audio_segment(audio_data, sample_rate, input_lang, timestamp):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    filename = f"data/audio_{timestamp}_{input_lang}.wav"
    
    audio_float = audio_data.astype(np.float32)
    audio_normalized = audio_float / np.max(np.abs(audio_float))
    gain = 0.5
    audio_amplified = audio_normalized * gain
    audio_clipped = np.clip(audio_amplified, -1, 1)
    
    sf.write(filename, audio_clipped, sample_rate)
    
    logger.info(f"Saved audio segment: {filename}")
