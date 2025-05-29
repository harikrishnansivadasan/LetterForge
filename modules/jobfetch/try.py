from modules.logging.logger import logger

try:
    1 / 0
except ZeroDivisionError as e:
    logger.error("An error occurred: %s", e)
