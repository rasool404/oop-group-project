from abc import ABC, abstractmethod

class BaseItem(ABC):
    def __init__(self, name, cost, effect_value):
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        if cost < 0:
            raise ValueError("Cost cannot be negative")
            
        self._name = name
        self._cost = max(0, cost)
        self._effect_value = effect_value
    
    @property
    def name(self):
        return self._name
        
    @property
    def cost(self):
        return self._cost
        
    @property
    def effect_value(self):
        return self._effect_value
        
    @abstractmethod
    def use(self, character):
        pass