from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure app
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app
