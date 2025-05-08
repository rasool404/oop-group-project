from models.base_task import BaseTask

class DailyTask(BaseTask):
    def calculate_reward(self):
        return 5
        
    def complete(self, success=True):
        self._completed = success
        return 5 if success else -5