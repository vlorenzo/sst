from flask import Flask

def create_app(input_lang='it', output_lang='en', use_gpt4_translation=False):
    app = Flask(__name__, template_folder='../templates')
    app.config['INPUT_LANG'] = input_lang
    app.config['OUTPUT_LANG'] = output_lang
    app.config['USE_GPT4_TRANSLATION'] = use_gpt4_translation

    print(f"App config: USE_GPT4_TRANSLATION = {app.config['USE_GPT4_TRANSLATION']}")  # Debug print
    
    from sst_app.app.routes import bp
    app.register_blueprint(bp)

    return app
