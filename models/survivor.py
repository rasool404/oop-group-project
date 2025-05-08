from models.base_character import BaseCharacter

class Survivor(BaseCharacter):
    def calculate_xp_needed(self):
        return 50 + (self._level - 1) * 10
        
    def level_up(self):
        if self._xp >= self.calculate_xp_needed():
            self._level += 1
            self._health = 30
            return True
        return False