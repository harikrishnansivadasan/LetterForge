import logging
import os
from datetime import datetime

"""Create log file name"""
LOG_FLE = f"{datetime.now().strftime('%Y-%m-%d')}.log"

"""Create path for log file"""
logs_path = os.path.join(os.getcwd(), "logs")

"""Create log file if it does not exist"""
os.makedirs(os.path.dirname(logs_path), exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FLE)

# Create a logger object
logger = logging.getLogger("LetterForge")
logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
