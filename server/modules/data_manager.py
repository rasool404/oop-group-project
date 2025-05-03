# data_manager.py
import json
import os
from datetime import datetime


class DataManager:
    """
    Utility class for managing data persistence.
    """
    
    def __init__(self, data_dir="data"):
        self._data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def save_tasks(self, tasks):
        """Save tasks to JSON file"""
        task_dicts = [task.to_dict() for task in tasks]
        with open(os.path.join(self._data_dir, "tasks.json"), "w") as f:
            json.dump(task_dicts, f, indent=2)
    
    def load_tasks(self, task_classes):
        """
        Load tasks from JSON file
        task_classes: Dictionary mapping task_type strings to task classes
        """
        try:
            with open(os.path.join(self._data_dir, "tasks.json"), "r") as f:
                task_dicts = json.load(f)
                
            tasks = []
            for task_dict in task_dicts:
                task_type = task_dict.get("task_type")
                if task_type in task_classes:
                    tasks.append(task_classes[task_type].from_dict(task_dict))
            return tasks
        except FileNotFoundError:
            return []  # Return empty list if file doesn't exist