# error_handler.py
from abc import ABC, abstractmethod
import logging
from datetime import datetime


class ErrorHandler(ABC):
    """
    Abstract base class for error handling in the application.
    Different types of errors are handled by specialized subclasses.
    """
    
    def __init__(self):
        self._last_error = None
        self._error_count = 0
        
        # Set up logging
        logging.basicConfig(
            filename='app_errors.log',
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self._logger = logging.getLogger(self.__class__.__name__)
    
    # Common error handling functionality
    def log_to_file(self, error, context=None):
        """Log error to file with context information"""
        self._error_count += 1
        self._last_error = {
            "error": str(error),
            "time": datetime.now().isoformat(),
            "context": context
        }
        
        # Log to file
        self._logger.error(f"Error: {error} | Context: {context}")
    
    @property
    def error_count(self):
        return self._error_count
    
    @property
    def last_error(self):
        return self._last_error
    
    # Abstract methods that must be implemented by derived classes
    @abstractmethod
    def handle_error(self, error, context=None):
        """
        Handle a specific type of error.
        Must be implemented by all derived classes.
        """
        pass
    
    @abstractmethod
    def log_error(self, error, context=None):
        """
        Log error details in a format appropriate for the error type.
        Must be implemented by all derived classes.
        """
        pass