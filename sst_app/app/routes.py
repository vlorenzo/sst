from flask import Blueprint, render_template, request, jsonify
from sst_app.audio.utils import process_audio
from sst_app.audio.processor import audio_queue, translation_queue
from sst_app.config import logger, CHUNK_DURATION, OVERLAP_DURATION
import time
import queue


bp = Blueprint('main', __name__)

#translation_result = None

@bp.route('/')
def index():
    return render_template('index.html', CHUNK_DURATION=CHUNK_DURATION, OVERLAP_DURATION=OVERLAP_DURATION)

@bp.route('/upload_audio', methods=['POST'])
def upload_audio():
    logger.info("Received audio upload request")
    if request.data:
        try:
            start_time = time.time()
            audio, process_duration = process_audio(request.data)
            input_lang = request.headers.get('X-Input-Lang', 'it')
            output_lang = request.headers.get('X-Output-Lang', 'en')
            audio_queue.put((audio, input_lang, output_lang))
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
        return jsonify(result)
    except queue.Empty:
        return jsonify({'translation': None})

@bp.route('/clear_queues', methods=['POST'])
def clear_queues():
    while not audio_queue.empty():
        audio_queue.get()
    while not translation_queue.empty():
        translation_queue.get()
    logger.info("Audio and translation queues cleared")
    return jsonify({'message': 'Queues cleared'}), 200

@bp.route('/reset_translation', methods=['POST'])
def reset_translation():
    global previous_transcript, new_session
    while not audio_queue.empty():
        audio_queue.get()
    while not translation_queue.empty():
        translation_queue.get()
    previous_transcript = ""
    new_session = True
    logger.info("Audio and translation queues cleared, previous transcript reset, and new session flag set")
    return jsonify({'message': 'Translation reset'}), 200
