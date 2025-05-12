from models.base_task import BaseTask
from datetime import datetime, date

class DailyTask(BaseTask):
    def __init__(self, title, description=""):
        self._title = title
        self._description = description
        self._completed = False
        self.last_completion_date = None
        self.was_successful = None  
        
    def complete(self, success=True):
        if self._completed:
            return "already_completed"
        self._completed = True
        self.was_successful = success  
        self.last_completion_date = datetime.now().strftime("%Y-%m-%d")
        return "completed"
        
    def calculate_reward(self):
        if not self._completed:
            return 0
        return 10 if self.was_successful else -5  
        
    def _last_completion_date(self):
        return self._last_completion_date
        
    def _completed(self):
        return self._completed
        
    def _description(self):
        return self._description
        
    def _title(self):
        return self._title