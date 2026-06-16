import logging
import os

# Set up the absolute path for the log file
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'optic.log')

# Ensure the directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure the root logger exactly once
def setup_logger(name="OpticCore"):
    logger = logging.getLogger(name)
    
    # Only add handlers if they don't already exist to prevent duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
        
        # File Handler (Saves to disk)
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Stream Handler (Prints to terminal)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
    return logger

# Create a default instance to import anywhere
optic_logger = setup_logger()