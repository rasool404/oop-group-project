from models.base_task import BaseTask
from datetime import date

class DailyTask(BaseTask):
    def __init__(self, title, description=""):
        super().__init__(title, description)
        self._last_completion_date = None
        
    def calculate_reward(self):
        return 5
        
    def complete(self, success=True):
        if self._completed:
            return "already_completed"  # Return a status code instead of printing
        self._completed = success
        self._last_completion_date = date.today()
        return "completed" if success else "failed"