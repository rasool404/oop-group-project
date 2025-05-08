from models.base_item import BaseItem

class Food(BaseItem):
    def use(self, character):
        character._hunger += self._effect_value

class Water(BaseItem):
    def use(self, character):
        character._thirst += self._effect_value

class Medicine(BaseItem):
    def use(self, character):
        character._infection -= self._effect_value