import logging
import sys

def setup_logger():
    logger = logging.getLogger('rag_logger')
    formatter = logging.Formatter('%(levelname)s - [%(asctime)s] - %(message)s', datefmt='%d/%b/%Y %H:%M:%S')
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

logger = setup_logger()
