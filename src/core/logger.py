"""
Logging system for My Kingdom game.
All logs are saved to the Logs folder with timestamps.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class GameLogger:
    """Centralized logging system for the game."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not GameLogger._initialized:
            self._setup_logger()
            GameLogger._initialized = True

    def _setup_logger(self):
        """Set up the logging configuration."""
        # Create Logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent.parent / "Logs"
        log_dir.mkdir(exist_ok=True)

        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"game_{timestamp}.log"

        # Configure logging
        self.logger = logging.getLogger("MyKingdom")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info("=" * 60)
        self.logger.info("Game Logger Initialized")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("=" * 60)

    def debug(self, message):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message):
        """Log critical message."""
        self.logger.critical(message)


# Global logger instance
logger = GameLogger()
