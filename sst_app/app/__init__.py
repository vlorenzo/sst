from flask import Flask
from sst_app.config import OVERLAP_DURATION

def create_app(input_lang='it', output_lang='en', use_gpt4_translation=False, use_overlapping_chunks=False):
    app = Flask(__name__, template_folder='../templates')
    app.config['INPUT_LANG'] = input_lang
    app.config['OUTPUT_LANG'] = output_lang
    app.config['USE_GPT4_TRANSLATION'] = use_gpt4_translation
    app.config['USE_OVERLAPPING_CHUNKS'] = use_overlapping_chunks
    app.config['OVERLAP_DURATION'] = OVERLAP_DURATION  # Add this line

    print(f"App config: USE_GPT4_TRANSLATION = {app.config['USE_GPT4_TRANSLATION']}")  # Debug print
    
    from sst_app.app.routes import bp
    app.register_blueprint(bp)

    return app
