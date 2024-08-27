from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import whisper
from googletrans import Translator
import numpy as np
from pydub import AudioSegment
import io
import threading
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")


# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)

# Load Whisper model
model = whisper.load_model("base")

# Initialize translator
translator = Translator()

# Audio buffer and processing settings
SAMPLE_RATE = 16000  # Whisper expects 16kHz audio
SEGMENT_DURATION = 10  # seconds
OVERLAP_DURATION = 5  # seconds
audio_buffer = []
buffer_lock = threading.Lock()

def process_audio(audio_blob):
    audio_bytes = io.BytesIO(audio_blob)
    audio = AudioSegment.from_wav(audio_bytes)
    audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(1)
    return np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0

def audio_processor():
    global audio_buffer
    while True:
        with buffer_lock:
            if len(audio_buffer) >= SEGMENT_DURATION * SAMPLE_RATE:
                segment = audio_buffer[:SEGMENT_DURATION * SAMPLE_RATE]
                audio_buffer = audio_buffer[SEGMENT_DURATION * SAMPLE_RATE - OVERLAP_DURATION * SAMPLE_RATE:]
            else:
                time.sleep(0.1)  # Wait a bit if not enough data
                continue

        try:
            result = model.transcribe(segment, language="es")
            transcription = result["text"]
            translation = translator.translate(transcription, src='es', dest='it').text
            socketio.emit('translation', {'text': translation})
        except Exception as e:
            print(f"Error processing audio: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio_data(data):
    global audio_buffer
    try:
        audio = process_audio(data)
        with buffer_lock:
            audio_buffer.extend(audio)
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        emit('error', {'message': 'Error processing audio'})

# if __name__ == '__main__':
#    threading.Thread(target=audio_processor, daemon=True).start()
#    socketio.run(app, debug=True)
    
if __name__ == '__main__':
    threading.Thread(target=audio_processor, daemon=True).start()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
    
