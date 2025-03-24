from openai import OpenAI
import os
import tempfile
import logging

# Get logger for this module
logger = logging.getLogger("audio_processing")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def process_voice_message(audio_file, target_language='en'):
    """
    Process an audio file to transcribe and summarize its content
    
    Args:
        audio_file: Audio file from request
        target_language: Target language for translation and summary (default: 'en')
        
    Returns:
        Dictionary with original transcription, translated text, and summary
    """
    logger.info(f"Processing audio file: {audio_file.filename}")
    logger.info(f"Target language: {target_language}")
    
    try:
        # Convert FileStorage to bytes for OpenAI API
        audio_bytes = audio_file.read()
        
        # Save to temporary file if needed for debugging
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(audio_bytes)
            logger.debug(f"Audio saved temporarily to: {temp_file_path}")
        
        # First, transcribe the audio using Whisper
        logger.info("Transcribing audio with Whisper")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=('audio.mp3', audio_bytes),  # Pass as tuple with filename
            response_format="text"
        )
        logger.info(f"Transcription complete: {len(transcript)} characters")
        
        # Enhanced system prompt for translation
        translation_system_prompt = f"""You are an expert translator specializing in legal terminology.

Your task is to translate the provided text into {target_language}, ensuring that:
1. Legal terminology is accurately translated using the appropriate terms in the target language
2. The meaning and nuance of the original text is preserved
3. The translation sounds natural to native speakers of {target_language}
4. Any culturally specific legal concepts are properly explained if direct equivalents don't exist

Maintain the same level of formality and technical precision as the original text while ensuring the translation is accessible to the intended audience.
"""
        
        # If target language is different from English, translate the transcript
        if target_language.lower() != 'en':
            logger.info(f"Translating transcript to {target_language}")
            translation_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": translation_system_prompt},
                    {"role": "user", "content": transcript}
                ]
            )
            translated_text = translation_response.choices[0].message.content
            logger.info("Translation complete")
        else:
            logger.info("No translation needed (target language is English)")
            translated_text = transcript
        
        # Enhanced system prompt for summary generation
        summary_system_prompt = """You are a legal assistant specializing in summarizing legal inquiries from transcribed audio.

Your task is to:
1. Identify the core legal question or issue being presented
2. Summarize the key facts and circumstances mentioned
3. Highlight any specific legal concerns or time-sensitive elements
4. Present this information in a clear, structured format

Guidelines for your summary:
- Focus on extracting legally relevant information
- Maintain the original meaning while removing filler words and repetition
- Organize information logically with clear paragraph breaks
- Prioritize facts, dates, parties involved, and specific legal questions
- Keep your summary concise yet complete

Your goal is to transform a potentially rambling verbal inquiry into a clear, focused summary that captures all legally significant elements.
"""
        
        # Get summary in target language
        logger.info("Generating summary")
        summary_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": summary_system_prompt},
                {"role": "user", "content": transcript}
            ]
        )
        
        summary_en = summary_response.choices[0].message.content
        logger.info("Summary generated")
        
        # Translate summary if needed
        if target_language.lower() != 'en':
            logger.info(f"Translating summary to {target_language}")
            summary_translation = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"Translate the following summary to {target_language}:"},
                    {"role": "user", "content": summary_en}
                ]
            )
            summary = summary_translation.choices[0].message.content
            logger.info("Summary translation complete")
        else:
            summary = summary_en
        
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
            logger.debug("Temporary audio file removed")
        except Exception as e:
            logger.warning(f"Could not remove temporary file: {str(e)}")
        
        logger.info("Audio processing complete")
        return {
            "original_transcription": transcript,
            "translated_text": translated_text,
            "summary": summary,
            "language": target_language
        }
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        raise Exception(f"Error processing audio: {str(e)}")
