import json
import os
from datetime import date
from models.survivor import Survivor
from models.todo_task import TodoTask
from models.daily_task import DailyTask

class DataManager:
    @staticmethod
    def save_game_state(character, tasks):
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
                "_completed": task._completed,
            }
            
            if isinstance(task, DailyTask):
                task_data["last_completion_date"] = task.last_completion_date
                task_data["was_successful"] = task.was_successful  # Save success status
            else:
                task_data["_priority"] = task._priority
                
            game_state["tasks"].append(task_data)
            
        with open("gamestate.json", "w") as f:
            json.dump(game_state, f, indent=4)
            
    @staticmethod
    def load_game_state():
        try:
            with open("gamestate.json", "r") as f:
                game_state = json.load(f)
                return game_state
        except FileNotFoundError:
            return None