from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import whisper
from googletrans import Translator
import numpy as np
from pydub import AudioSegment
import io
import queue
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Load Whisper model
model = whisper.load_model("base")

# Initialize translator
translator = Translator()

# Audio buffer
audio_buffer = queue.Queue()

# Buffer settings
SEGMENT_LENGTH = 10  # seconds
OVERLAP = 5  # seconds

def process_audio(audio_blob):
    audio_bytes = io.BytesIO(audio_blob)
    audio = AudioSegment.from_wav(audio_bytes)
    audio_array = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
    return audio_array

def audio_processor():
    while True:
        if audio_buffer.qsize() >= SEGMENT_LENGTH:
            segment = []
            for _ in range(SEGMENT_LENGTH):
                segment.extend(audio_buffer.get())
            
            # Process the segment
            result = model.transcribe(np.array(segment), language="es")
            transcription = result["text"]
            translation = translator.translate(transcription, src='es', dest='it').text
            
            socketio.emit('translation', {'text': translation})
            
            # Put back the overlapping part
            for _ in range(OVERLAP):
                audio_buffer.put(segment.pop(0))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio_data(data):
    try:
        audio = process_audio(data)
        for sample in audio:
            audio_buffer.put(sample)
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        emit('error', {'message': 'Error processing audio'})

if __name__ == '__main__':
    threading.Thread(target=audio_processor, daemon=True).start()
    socketio.run(app, debug=True)
