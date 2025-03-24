import os
import sys
import logging
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Reduce Flask's internal logging
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# Get logger
logger = logging.getLogger("app")

def create_app():
    app = Flask(__name__)
    
    # Import and register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    logger.info("Application initialized")
    return app

if __name__ == '__main__':
    logger.info("Starting application")
    app = create_app()
    app.run(debug=True)
