import logging
import os
from datetime import datetime

"""Create log file name"""
LOG_FLE = f"{datetime.now().strftime('%Y-%m-%d')}.log"

"""Create path for log file"""
logs_path = os.path.join(os.getcwd(), "logs")

"""Create log file if it does not exist"""
os.makedirs(os.path.dirname(logs_path), exist_ok=True)

LOG_FLE_PATH = os.path.join(logs_path, LOG_FLE)
logging.basicConfig(
    filename=LOG_FLE_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    logging.info("Logging is set up.")
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
