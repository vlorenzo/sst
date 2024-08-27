from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import whisper
from googletrans import Translator
import numpy as np
from pydub import AudioSegment
import io

app = Flask(__name__)
socketio = SocketIO(app)

# Load Whisper model
model = whisper.load_model("base")

# Initialize translator
translator = Translator()

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

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio_data(data):
    try:
        # Process audio data
        audio = process_audio(data)
        
        # Transcribe audio using Whisper (specifying Spanish as the source language)
        result = model.transcribe(audio, language="es")
        transcription = result["text"]
        
        # Translate transcription from Spanish to Italian
        translation = translator.translate(transcription, src='es', dest='it').text
        
        # Emit the translation to the client
        emit('translation', {'text': translation})
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        emit('error', {'message': 'Error processing audio'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
