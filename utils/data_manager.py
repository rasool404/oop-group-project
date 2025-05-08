import json
import os
from datetime import date
from models.survivor import Survivor
from models.todo_task import TodoTask
from models.daily_task import DailyTask

class DataManager:
    @staticmethod
    def save_game_state(character, tasks):
        try:
            game_state = {
                "character": {
                    "_name": character._name,
                    "_level": character._level,
                    "_xp": character._xp,
                    "_health": character._health,
                    "_hunger": character._hunger,
                    "_thirst": character._thirst,
                    "_infection": character._infection
                },
                "tasks": []
            }
            
            for task in tasks:
                task_data = {
                    "_title": task._title,
                    "_description": task._description,
                    "_completed": task._completed
                }
                
                if isinstance(task, TodoTask):
                    task_data["priority"] = task._priority
                elif isinstance(task, DailyTask) and task._last_completion_date:
                    task_data["last_completion_date"] = task._last_completion_date.isoformat()
                    
                game_state["tasks"].append(task_data)
                
            # Create a backup of the existing file if it exists
            if os.path.exists("gamestate.json"):
                try:
                    os.rename("gamestate.json", "gamestate.json.bak")
                except:
                    pass
                    
            # Write new data
            with open("gamestate.json", "w") as f:
                json.dump(game_state, f, indent=4)
                
            # Remove backup if save was successful
            if os.path.exists("gamestate.json.bak"):
                try:
                    os.remove("gamestate.json.bak")
                except:
                    pass
                    
        except Exception as e:
            # Restore backup if save failed
            if os.path.exists("gamestate.json.bak"):
                try:
                    if os.path.exists("gamestate.json"):
                        os.remove("gamestate.json")
                    os.rename("gamestate.json.bak", "gamestate.json")
                except:
                    pass
            raise Exception(f"Failed to save game state: {str(e)}")
            
    @staticmethod
    def load_game_state(filename="gamestate.json"):
        try:
            if not os.path.exists(filename):
                return None
                
            with open(filename, "r") as f:
                try:
                    game_state = json.load(f)
                except json.JSONDecodeError:
                    # If file is corrupted, try loading backup
                    if os.path.exists(filename + ".bak"):
                        with open(filename + ".bak", "r") as backup:
                            game_state = json.load(backup)
                    else:
                        return None
                
            # Convert ISO date strings back to date objects for daily tasks
            for task_data in game_state["tasks"]:
                if "last_completion_date" in task_data:
                    task_data["last_completion_date"] = date.fromisoformat(task_data["last_completion_date"])
                    
            return game_state
            
        except Exception as e:
            # If loading fails completely, return None to start fresh
            return None