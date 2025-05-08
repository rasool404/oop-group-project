from abc import ABC, abstractmethod

class BaseCharacter(ABC):
    def __init__(self, name, level=1, xp=0, health=30):
        self._name = name
        self._level = max(1, level)
        self._xp = max(0, xp)
        self._health = min(max(0, health), 30)
        self._hunger = 100
        self._thirst = 100
        self._infection = 0
        
    @abstractmethod
    def calculate_xp_needed(self):
        pass
        
    @abstractmethod
    def level_up(self):
        pass
    
    # Getters
    @property
    def name(self):
        return self._name
        
    @property
    def level(self):
        return self._level
        
    @property
    def xp(self):
        return self._xp
        
    @property
    def health(self):
        return self._health
        
    @property
    def hunger(self):
        return self._hunger
        
    @property
    def thirst(self):
        return self._thirst
        
    @property
    def infection(self):
        return self._infection
    
    # Setters with validation
    @xp.setter
    def xp(self, value):
        self._xp = max(0, value)
        
    @health.setter
    def health(self, value):
        self._health = min(max(0, value), 30)
        
    @hunger.setter
    def hunger(self, value):
        self._hunger = min(max(0, value), 100)
        
    @thirst.setter
    def thirst(self, value):
        self._thirst = min(max(0, value), 100)
        
    @infection.setter
    def infection(self, value):
        self._infection = min(max(0, value), 100)