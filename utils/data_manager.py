import json
import os

class DataManager:
    @staticmethod
    def save_game_state(character, tasks, filename="gamestate.json"):
        try:
            game_state = {
                "character": character.__dict__,
                "tasks": [task.__dict__ for task in tasks]
            }
            with open(filename, 'w') as f:
                json.dump(game_state, f)
        except Exception as e:
            raise Exception(f"Failed to save game state: {str(e)}")
    
    @staticmethod
    def load_game_state(filename="gamestate.json"):
        try:
            if not os.path.exists(filename):
                return None
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load game state: {str(e)}")