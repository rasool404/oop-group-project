from abc import ABC, abstractmethod
from datetime import datetime


class Task(ABC):
    """
    Abstract base class for all types of tasks in the post-apocalyptic to-do system.
    """
    
    def __init__(self, title, description, priority=1):
        self._id = None  # Will be set when saved to database
        self._title = title
        self._description = description
        self._priority = priority  # 1-3 scale (1=low, 3=high)
        self._completed = False
        self._created_date = datetime.now()
        self._completed_date = None
    
    # Getters and setters for encapsulation
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        if not value:
            raise ValueError("Task title cannot be empty")
        self._title = value
    
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = value
    
    @property
    def priority(self):
        return self._priority
    
    @priority.setter
    def priority(self, value):
        if value not in [1, 2, 3]:
            raise ValueError("Priority must be between 1 and 3")
        self._priority = value
    
    @property
    def completed(self):
        return self._completed
    
    # Common methods for all tasks
    def mark_complete(self):
        """Mark the task as completed and calculate rewards"""
        if not self._completed:
            self._completed = True
            self._completed_date = datetime.now()
            return self.complete()
        return None
    
    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "priority": self._priority,
            "completed": self._completed,
            "created_date": self._created_date.isoformat(),
            "completed_date": self._completed_date.isoformat() if self._completed_date else None,
            "task_type": self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create task from dictionary (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement this method")
    
    # Abstract methods that must be implemented by derived classes
    @abstractmethod
    def complete(self):
        """
        Logic for task completion. Returns rewards for completing the task.
        Must be implemented by all derived classes.
        """
        pass
    
    @abstractmethod
    def calculate_reward(self):
        """
        Calculate the rewards for completing this task.
        Must be implemented by all derived classes.
        """
        pass