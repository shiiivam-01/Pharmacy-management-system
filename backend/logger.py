"""
Logging configuration for the Pharmacy Management System.
"""
import logging
from logging.handlers import RotatingFileHandler
from backend import config

def get_logger(name: str) -> logging.Logger:
    """
    Creates or retrieves a logger configured to output to both console and a rotating file.
    
    Args:
        name: The name of the logger (usually __name__).
        
    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    
    # Only configure if no handlers are present to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Ensure log directory exists
        config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Rotating File Handler (1 MB, up to 5 backups)
        log_file = config.LOGS_DIR / "pms.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger
