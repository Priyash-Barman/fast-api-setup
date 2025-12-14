import logging

from config import APP_NAME

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Format
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] - %(name)s - %(message)s"
)
console_handler.setFormatter(formatter)

# Add the handler if not already added
if not logger.handlers:
    logger.addHandler(console_handler)
