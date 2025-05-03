# input_validation_handler.py
from error_handler import ErrorHandler


class InputValidationHandler(ErrorHandler):
    """
    Handler for input validation errors.
    """
    
    def __init__(self):
        super().__init__()
        self._validation_errors = []
    
    def handle_error(self, error, context=None):
        """
        Handle input validation error
        """
        error_info = {
            "message": str(error),
            "field": context.get("field") if context else None,
            "value": context.get("value") if context else None
        }
        
        self._validation_errors.append(error_info)
        self.log_error(error, context)
        
        return error_info
    
    def log_error(self, error, context=None):
        """
        Log validation error with additional context
        """
        field = context.get("field") if context else "unknown"
        value = context.get("value") if context else "unknown"
        
        message = f"Validation error in field '{field}' with value '{value}': {error}"
        self.log_to_file(error, {"message": message, "context": context})
    
    def get_validation_errors(self):
        """Get all validation errors"""
        return self._validation_errors
    
    def clear_errors(self):
        """Clear validation errors"""
        self._validation_errors = []