from models.base_task import BaseTask

class TodoTask(BaseTask):
    def __init__(self, title, description, priority="low"):
        super().__init__(title, description)
        self._priority = priority
        
    def calculate_reward(self):
        rewards = {"low": 3, "medium": 5, "high": 7}
        return rewards[self._priority]
        
    def complete(self):
        if self._completed:
            return "already_completed"  # Return a status code instead of printing
        self._completed = True
        return "completed"
        return self.calculate_reward()