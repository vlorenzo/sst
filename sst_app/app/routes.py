from flask import Blueprint, render_template, request, jsonify
from sst_app.audio.utils import process_audio
from sst_app.audio.processor import audio_queue, translation_queue
from sst_app.config import logger
import time
import queue


bp = Blueprint('main', __name__)

#translation_result = None

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload_audio', methods=['POST'])
def upload_audio():
    logger.info("Received audio upload request")
    if request.data:
        try:
            start_time = time.time()
            audio, process_duration = process_audio(request.data)
            audio_queue.put(audio)
            total_duration = time.time() - start_time
            logger.info(f"Audio upload and initial processing completed in {total_duration:.2f} seconds")
            return jsonify({
                'message': 'Audio received and processing',
                'audio_process_time': process_duration,
                'total_upload_time': total_duration
            }), 200
        except Exception as e:
            logger.error(f"Error processing uploaded audio: {str(e)}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'No audio data received'}), 400



@bp.route('/get_translation')
def get_translation():
    logger.info("Received translation request")
    try:
        result = translation_queue.get_nowait()
        logger.info(f"Sending translation: {result}")
        return jsonify({'translation': result})
    except queue.Empty:
        return jsonify({'translation': None})
