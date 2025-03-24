from flask import Blueprint, request, jsonify
from app.utils.text_data_util import structure_legal_inquiry, analyze_document, get_legal_faq_response
from app.utils.audio_data_util import process_voice_message
import json
import os
import logging

# Get logger for this module
logger = logging.getLogger("api")

main = Blueprint('main', __name__)

@main.route('/api/structure-inquiry', methods=['POST'])
def structure_inquiry():
    logger.info("Legal inquiry structuring API called")
    
    try:
        data = request.json
        if not data:
            logger.warning("No JSON data provided in request")
            return jsonify({'error': 'No data provided'}), 400
            
        question = data.get('question')
        if not question:
            logger.warning("No question provided in request")
            return jsonify({'error': 'No question provided'}), 400
        
        if len(question.strip()) < 10:
            logger.warning(f"Question too short: '{question}'")
            return jsonify({'error': 'Question is too short. Please provide more details.'}), 400
            
        logger.info(f"Processing legal inquiry: {question[:50]}...")
        structured_response = structure_legal_inquiry(question)
        logger.info("Legal inquiry structuring completed successfully")
        return jsonify(structured_response)
    except Exception as e:
        logger.error(f"Error in legal inquiry structuring: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@main.route('/api/analyze-document', methods=['POST'])
def analyze_document_route():
    logger.info("Document analysis API called")
    
    try:
        if 'document' not in request.files:
            logger.warning("No document provided in request")
            return jsonify({'error': 'No document provided'}), 400
            
        file = request.files['document']
            
        # Validate file
        if file.filename == '':
            logger.warning("File has no filename")
            return jsonify({'error': 'File has no filename'}), 400
        
        # Check file extension
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = os.path.splitext(file.filename.lower())[1]
        
        if file_ext not in allowed_extensions:
            logger.warning(f"Unsupported file type: {file_ext}")
            return jsonify({
                'error': f'Unsupported file type. Allowed types: {", ".join(allowed_extensions)}'
            }), 400
        
        logger.info(f"Processing file: {file.filename}")
        analysis = analyze_document(file)
        logger.info("Document analysis completed successfully")
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error in document analysis: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@main.route('/api/process-voice', methods=['POST'])
def process_voice():
    logger.info("Voice processing API called")
    
    try:
        if 'audio' not in request.files:
            logger.warning("No audio file provided in request")
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        target_language = request.form.get('language', 'en')  # Default to English
        
        if audio_file.filename == '':
            logger.warning("Audio file has no filename")
            return jsonify({'error': 'No selected file'}), 400
        
        # Check file extension
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg']
        file_ext = os.path.splitext(audio_file.filename.lower())[1]
        
        if file_ext not in allowed_extensions:
            logger.warning(f"Unsupported audio file type: {file_ext}")
            return jsonify({
                'error': f'Unsupported audio file type. Allowed types: {", ".join(allowed_extensions)}'
            }), 400
            
        logger.info(f"Processing audio file: {audio_file.filename} in language: {target_language}")
        result = process_voice_message(audio_file, target_language)
        logger.info("Voice processing completed successfully")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in voice processing: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@main.route('/api/legal-faq', methods=['POST'])
def legal_faq():
    logger.info("Legal FAQ API called")
    
    try:
        data = request.json
        if not data:
            logger.warning("No JSON data provided in request")
            return jsonify({'error': 'No data provided'}), 400
            
        question = data.get('question')
        if not question:
            logger.warning("No question provided in request")
            return jsonify({'error': 'No question provided'}), 400
        
        if len(question.strip()) < 10:
            logger.warning(f"Question too short: '{question}'")
            return jsonify({'error': 'Question is too short. Please provide more details.'}), 400
            
        logger.info(f"Processing legal FAQ: {question[:50]}...")
        response = get_legal_faq_response(question)
        logger.info("Legal FAQ response generated successfully")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in legal FAQ: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
