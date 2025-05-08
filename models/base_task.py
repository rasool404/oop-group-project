from abc import ABC, abstractmethod

class BaseTask(ABC):
    def __init__(self, title, description=""):  # Set default empty string for description
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
            
        self._title = title.strip()
        self._description = description if description else ""
        self._completed = False
        
    @property
    def title(self):
        return self._title
        
    @property
    def description(self):
        return self._description
        
    @property
    def completed(self):
        return self._completed
        
    @completed.setter
    def completed(self, value):
        if not isinstance(value, bool):
            raise ValueError("Completed status must be a boolean")
        self._completed = value
        
    @abstractmethod
    def complete(self):
        pass
        
    @abstractmethod
    def calculate_reward(self):
        pass