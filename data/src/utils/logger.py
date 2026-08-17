"""
Sistemdeki olayları ve hataları dosyaya kaydeden loglama aracı.
"""
import logging
import os
from datetime import datetime


def setup_logger():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{datetime.now().strftime('%Y-%m-%d')}_app.log"
    log_filepath = os.path.join(log_dir, log_filename)

    logger = logging.getLogger('KonyaVeriBotu')
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
