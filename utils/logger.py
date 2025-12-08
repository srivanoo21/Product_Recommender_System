"""
Logger Utility Script
---------------------
This script provides a reusable logger setup for the product recommender system.
- Configures logging format, level, and file output.
- Ensures consistent logging across all modules for debugging and monitoring.
- Used throughout the project to record info, warnings, errors, and debug messages.
"""

import logging
import os
from datetime import datetime

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR,exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger