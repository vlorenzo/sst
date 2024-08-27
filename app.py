from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import whisper
from googletrans import Translator
from audio_processing import process_audio

app = Flask(__name__)
socketio = SocketIO(app)

# Load Whisper model
model = whisper.load_model("base")

# Initialize translator
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio_data(data):
    # Process audio data
    audio = process_audio(data)
    
    # Transcribe audio using Whisper
    result = model.transcribe(audio)
    transcription = result["text"]
    
    # Translate transcription
    translation = translator.translate(transcription, dest='es').text  # Change 'es' to desired language code
    
    # Emit the translation to the client
    emit('translation', {'text': translation})

if __name__ == '__main__':
    socketio.run(app, debug=True)
