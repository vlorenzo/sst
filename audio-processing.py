import numpy as np
from pydub import AudioSegment
import io

def process_audio(audio_blob):
    # Convert blob to bytes
    audio_bytes = io.BytesIO(audio_blob)

    # Load audio using pydub
    audio = AudioSegment.from_wav(audio_bytes)

    # Convert to numpy array
    audio_array = np.array(audio.get_array_of_samples())

    # Normalize
    audio_array = audio_array.astype(np.float32) / 32768.0

    # Reshape if stereo
    if audio.channels == 2:
        audio_array = audio_array.reshape((-1, 2))

    return audio_array
