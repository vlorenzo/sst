from flask import Flask
from sst_app.config import OVERLAP_DURATION

def create_app(input_lang='it', output_lang='en', use_gpt4_translation=False, use_overlapping_chunks=True, whisper_model='openai'):
    app = Flask(__name__, template_folder='../templates')
    app.config['INPUT_LANG'] = input_lang
    app.config['OUTPUT_LANG'] = output_lang
    app.config['USE_GPT4_TRANSLATION'] = use_gpt4_translation
    app.config['USE_OVERLAPPING_CHUNKS'] = use_overlapping_chunks
    app.config['OVERLAP_DURATION'] = OVERLAP_DURATION
    app.config['WHISPER_MODEL'] = whisper_model

    print(f"App config: USE_GPT4_TRANSLATION = {app.config['USE_GPT4_TRANSLATION']}, WHISPER_MODEL = {app.config['WHISPER_MODEL']}")

    from sst_app.app.routes import bp
    app.register_blueprint(bp)

    return app
