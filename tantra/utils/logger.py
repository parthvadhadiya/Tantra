import logging
import sys


def setup_logger(name: str) -> logging.Logger:
    """Setup a logger with consistent formatting"""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Always set to DEBUG
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)  # Handler also at DEBUG level
    
    # Create formatter
    formatter = logging.Formatter(
        '\n[%(asctime)s] %(name)s.%(funcName)s:%(lineno)d\n%(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

# Global logger instance
logger = setup_logger("tantra")
