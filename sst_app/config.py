import logging

# Audio processing settings
SAMPLE_RATE = 16000  # Whisper expects 16kHz audio
CHUNK_DURATION = 3  # Process 3 seconds of audio at a time
AUDIO_DTYPE = 'float32'
OVERLAP_DURATION = 1  # 1 second overlap

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Whisper prompt
STATIC_PROMPT = """
Nomi: Lorenzo, Lorenzo Verna, Twiper, AGER, Bologna.
Acronimi: CTO (Chief Technology Officer)
Termini Tecnici: AGER, Evento AGER, Artificial Intelligence, SST (Simultaneous Speech Translator).
Frase di saluto: Buongiorno a tutti, sono Lorenzo Verna, CTO di Twiper. Benvenuti al Evento AGER. E' un piacere condividere con voi. le nostre soluzioni di Intelligenza Artificale applicate al vostro business. 
"""
