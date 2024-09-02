import logging

# Audio processing settings
SAMPLE_RATE = 16000  # Whisper expects 16kHz audio
CHUNK_DURATION = 4  # Process 4 seconds of audio at a time
OVERLAP_DURATION = 1  # 1 second overlap
AUDIO_DTYPE = 'float32'
USE_OVERLAPPING_CHUNKS = True  # Add this line to enable/disable overlapping chunks
# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add a file handler to save logs to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Whisper prompt
STATIC_PROMPT = """
Nomi: Lorenzo, Lorenzo Verna, Twiper, AGER, Bologna.
Acronimi: CTO (Chief Technology Officer)
Termini Tecnici: AGER, Evento AGER, Artificial Intelligence, SST (Simultaneous Speech Translator).
Frase di saluto: Buongiorno a tutti, sono Lorenzo Verna, CTO di Twiper. Benvenuti al Evento AGER. E' un piacere condividere con voi. le nostre soluzioni di Intelligenza Artificale applicate al vostro business. 
"""
