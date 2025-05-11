from typing import List
from .todo_task import TodoTask
from .daily_task import DailyTask
from .survivor import Survivor

class TaskManager:
    def __init__(self):
        self._tasks: List[TodoTask | DailyTask] = []
    
    def create_task(self, task_type: str, title: str, description: str, priority: str = "low") -> bool:
        if not title.strip():
            return False
            
        if task_type == "todo":
            task = TodoTask(title, description, priority)
        else:
            task = DailyTask(title, description)
            
        self._tasks.append(task)
        return True
    
    def delete_task(self, task_idx: int) -> bool:
        if 0 <= task_idx < len(self._tasks):
            self._tasks.pop(task_idx)
            return True
        return False
    
    def complete_task(self, task_idx: int, character: Survivor, success: bool = True) -> tuple[str, int]:
        if not (0 <= task_idx < len(self._tasks)):
            return "invalid_index", 0
            
        task = self._tasks[task_idx]
        
        if isinstance(task, DailyTask):
            status = task.complete(success)
        else:
            status = task.complete()
            
        if status == "already_completed":
            return status, 0
            
        reward = task.calculate_reward() if status == "completed" else -5
        return status, reward
    
    def get_tasks(self) -> List[TodoTask | DailyTask]:
        return self._tasks
    
    def clear_tasks(self) -> None:
        self._tasks.clear()
    
    def load_tasks(self, tasks_data: list) -> None:
        self._tasks.clear()
        for task_data in tasks_data:
            if "priority" in task_data:
                task = TodoTask(task_data["_title"], task_data["_description"], 
                              task_data.get("_priority", "low"))
            else:
                task = DailyTask(task_data["_title"], task_data["_description"])
            task._completed = task_data["_completed"]
            self._tasks.append(task)