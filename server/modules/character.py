# character.py
from abc import ABC, abstractmethod


class Character(ABC):
    """
    Abstract base class for different character types in the post-apocalyptic world.
    """
    
    def __init__(self, name):
        self._name = name
        self._health = 100
        self._max_health = 100
        self._level = 1
        self._experience = 0
        self._experience_to_level = 100  # XP needed for first level up
        
        # Base stats
        self._strength = 10  # Affects carrying capacity and physical tasks
        self._intelligence = 10  # Affects crafting and complex tasks
        self._agility = 10  # Affects chances to avoid dangers
        
        # Resource bonuses (can be modified by character type)
        self._resource_bonus = {
            "food": 1.0,
            "water": 1.0,
            "medicine": 1.0,
            "scrap": 1.0,
            "ammo": 1.0
        }
    
    # Getters and setters for encapsulation
    @property
    def name(self):
        return self._name
    
    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        if value > self._max_health:
            self._health = self._max_health
        elif value < 0:
            self._health = 0
        else:
            self._health = value
    
    @property
    def level(self):
        return self._level
    
    @property
    def experience(self):
        return self._experience
    
    @property
    def strength(self):
        return self._strength
    
    @property
    def intelligence(self):
        return self._intelligence
    
    @property
    def agility(self):
        return self._agility
    
    # Common methods for all characters
    def add_experience(self, amount):
        """
        Add experience to the character and level up if necessary
        """
        self._experience += amount
        
        # Check if we should level up
        while self._experience >= self._experience_to_level:
            self._experience -= self._experience_to_level
            self.level_up()
            # Increase XP needed for next level
            self._experience_to_level = int(self._experience_to_level * 1.5)
    
    def get_resource_bonus(self, resource_type):
        """
        Get the bonus multiplier for a specific resource type
        """
        return self._resource_bonus.get(resource_type, 1.0)
    
    def to_dict(self):
        """Convert character to dictionary for JSON serialization"""
        return {
            "name": self._name,
            "health": self._health,
            "max_health": self._max_health,
            "level": self._level,
            "experience": self._experience,
            "experience_to_level": self._experience_to_level,
            "strength": self._strength,
            "intelligence": self._intelligence,
            "agility": self._agility,
            "resource_bonus": self._resource_bonus,
            "character_type": self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create character from dictionary (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement this method")
    
    # Abstract methods that must be implemented by derived classes
    @abstractmethod
    def level_up(self):
        """
        Logic for leveling up the character. Each character type handles stat increases differently.
        Must be implemented by all derived classes.
        """
        pass
    
    @abstractmethod
    def gain_experience(self, task_type):
        """
        Calculate experience gained based on task type and character specialization.
        Must be implemented by all derived classes.
        """
        pass