import logging
import os

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.DEBUG

def setup_logger(log_file='application.log'):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        filename=os.path.join('logs', log_file),
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        filemode='a'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    logging.getLogger().addHandler(console_handler)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def log_warning(message):
    logging.warning(message)

def log_debug(message):
    logging.debug(message)