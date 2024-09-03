import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sst_app.app import create_app
from sst_app.audio.processor import start_audio_processor

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Speech-to-Text and Translation App')
    parser.add_argument('--input_lang', default='it', help='Input language code (default: it)')
    parser.add_argument('--output_lang', default='en', help='Output language code (default: en)')
    parser.add_argument('--use_overlapping_chunks', action='store_true', help='Enable overlapping chunks (default: False)')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the Flask app on (default: 5000)')
    args = parser.parse_args()

    app = create_app(input_lang=args.input_lang, output_lang=args.output_lang, use_gpt4_translation=True, use_overlapping_chunks=args.use_overlapping_chunks)
    start_audio_processor(app)
    
    app.run(debug=True, use_reloader=False, port=args.port)
