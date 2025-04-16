import logging.config
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.config.fileConfig(
        fname='config/logging.conf',
        disable_existing_loggers=False
    )

def get_logger(name: str = "appLogger"):
    return logging.getLogger(name)
