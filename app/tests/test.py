import sys
import logging
from pathlib import Path

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app import create_app
import io

# Get logger for tests
logger = logging.getLogger("test")

logger.info("Initializing test application")
app = create_app()
client = app.test_client()

def analyze_document():
    """Test document analysis API"""
    logger.info("=== TESTING DOCUMENT ANALYSIS API ===")
    
    # Get path to test documents folder
    base_dir = Path(__file__).parent.parent.parent
    docs_folder = base_dir / 'test_documents'
    
    # Get test document
    doc_files = list(docs_folder.glob('*.*'))
    
    if not doc_files:
        logger.warning("No documents found in test_documents folder!")
        return
        
    logger.info(f"Found document: {doc_files[0].name}")
    
    with open(doc_files[0], 'rb') as f:
        data = {
            'document': (io.BytesIO(f.read()), doc_files[0].name)
        }
        
        logger.info(f"Sending document to API: {doc_files[0].name}")
        response = client.post('/api/analyze-document',
                             data=data, 
                             content_type='multipart/form-data')
        
        logger.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json
            logger.info(f"Document analysis successful")
            print(f"\nFilename: {result['filename']}")
            print("\nSummary:")
            print(result['summary'])
            print("\nKey Facts:")
            for i, fact in enumerate(result['key_facts'], 1):
                print(f"{i}. {fact}")
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(f"Error details: {response.json}")
            print(f"Error: {response.status_code}")
            print(response.json)

def process_audio():
    """Test voice processing API"""
    logger.info("=== TESTING VOICE PROCESSING API ===")
    
    # Get path to audio_data folder
    base_dir = Path(__file__).parent.parent.parent
    audio_folder = base_dir / 'audio_data'
    
    # Get audio file
    audio_files = list(audio_folder.glob('*.*'))
    
    if not audio_files:
        logger.warning("No audio files found in audio_data folder!")
        return
        
    logger.info(f"Found audio file: {audio_files[0].name}")
    
    with open(audio_files[0], 'rb') as f:
        data = {
            'audio': (io.BytesIO(f.read()), audio_files[0].name),
            'language': 'es'  # Test Spanish translation
        }
        
        logger.info(f"Sending audio to API: {audio_files[0].name}")
        response = client.post('/api/process-voice',
                             data=data,
                             content_type='multipart/form-data')
        
        logger.info(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json
            logger.info("Audio processing successful")
            print("\nOriginal Transcription:")
            print(result['original_transcription'])
            print("\nSpanish Translation:")
            print(result['translated_text'])
            print("\nSpanish Summary:")
            print(result['summary'])
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(f"Error details: {response.json}")
            print(f"Error: {response.status_code}")
            print(response.json)

def test_legal_inquiry():
    """Test legal inquiry API"""
    logger.info("=== TESTING LEGAL INQUIRY API ===")
    
    question = "I have a problem with my landlord, he won't fix my heating for 2 months and now it's winter and I'm freezing"
    logger.info(f"Testing question: {question}")
    
    response = client.post('/api/structure-inquiry',
                          json={"question": question})
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json
        logger.info("Legal inquiry structuring successful")
        print("\nOriginal Question:")
        print(question)
        print("\nStructured Question:")
        print(result['structured_question'])
        print("\nLegal Issues:")
        for i, issue in enumerate(result['legal_issues'], 1):
            print(f"{i}. {issue}")
        print("\nSuggested Categories:")
        for i, category in enumerate(result['suggested_categories'], 1):
            print(f"{i}. {category}")
        print("\nMissing Information:")
        for i, info in enumerate(result['missing_information'], 1):
            print(f"{i}. {info}")
    else:
        logger.error(f"Error: {response.status_code}")
        logger.error(f"Error details: {response.json}")
        print(f"Error: {response.status_code}")
        print(response.json)

def test_legal_faq():
    """Test legal FAQ API"""
    logger.info("=== TESTING LEGAL FAQ API ===")
    
    question = "How long do I have to file a personal injury claim in California?"
    logger.info(f"Testing question: {question}")
    
    response = client.post('/api/legal-faq',
                          json={"question": question})
    
    logger.info(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json
        logger.info("Legal FAQ response successful")
        print("\nQuestion:")
        print(question)
        print("\nAnswer:")
        print(result['answer'])
        if 'references' in result and result['references']:
            print("\nReferences:")
            for i, ref in enumerate(result['references'], 1):
                print(f"{i}. {ref}")
    else:
        logger.error(f"Error: {response.status_code}")
        logger.error(f"Error details: {response.json}")
        print(f"Error: {response.status_code}")
        print(response.json)

if __name__ == "__main__":
    logger.info("Starting document analysis test")
    analyze_document()
    process_audio()
    test_legal_inquiry()
    test_legal_faq()
    logger.info("Test completed")

