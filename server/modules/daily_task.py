# daily_task.py
from datetime import datetime, timedelta
from task import Task


class DailyTask(Task):
    """
    A task that recurs daily. Provides small, consistent rewards.
    """
    
    def __init__(self, title, description, priority=1):
        super().__init__(title, description, priority)
        self._streak = 0  # Number of consecutive days completed
        self._last_completed = None
        self._reset_time = datetime.now() + timedelta(days=1)  # Next day by default
    
    @property
    def streak(self):
        return self._streak
    
    @property
    def reset_time(self):
        return self._reset_time
    
    def reset(self):
        """Reset the task to be completed again"""
        if self._completed:
            self._completed = False
            self._completed_date = None
            self._reset_time = datetime.now() + timedelta(days=1)
    
    def check_streak(self):
        """Check if streak is maintained or broken"""
        if self._last_completed:
            # If more than 48 hours have passed, streak is broken
            time_diff = datetime.now() - self._last_completed
            if time_diff.total_seconds() > 48 * 3600:
                self._streak = 0
    
    def complete(self):
        """
        Complete the daily task, update streak, and calculate rewards.
        """
        self.check_streak()
        
        # Update streak
        if not self._last_completed or (datetime.now() - self._last_completed).days >= 1:
            self._streak += 1
        
        self._last_completed = datetime.now()
        
        # Calculate and return rewards
        return self.calculate_reward()
    
    def calculate_reward(self):
        """
        Calculate rewards based on priority and streak.
        Returns a dictionary of resources and experience.
        """
        # Base XP based on priority
        base_xp = 10 * self._priority
        
        # Bonus for streak
        streak_bonus = min(self._streak * 0.1, 1.0)  # Up to 100% bonus
        
        # Calculate resources based on priority
        resources = {
            "food": 2 * self._priority,
            "water": 2 * self._priority,
            "medicine": 1 * self._priority if self._priority > 1 else 0,
            "scrap": 1 * self._priority if self._priority > 1 else 0
        }
        
        # Apply streak bonus
        for key in resources:
            resources[key] = int(resources[key] * (1 + streak_bonus))
        
        return {
            "experience": int(base_xp * (1 + streak_bonus)),
            "resources": resources,
            "message": f"Daily task completed! Streak: {self._streak}"
        }
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = super().to_dict()
        data.update({
            "streak": self._streak,
            "last_completed": self._last_completed.isoformat() if self._last_completed else None,
            "reset_time": self._reset_time.isoformat()
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create DailyTask from dictionary"""
        task = cls(data["title"], data["description"], data["priority"])
        task.id = data["id"]
        task._completed = data["completed"]
        task._created_date = datetime.fromisoformat(data["created_date"])
        task._completed_date = datetime.fromisoformat(data["completed_date"]) if data["completed_date"] else None
        task._streak = data["streak"]
        task._last_completed = datetime.fromisoformat(data["last_completed"]) if data["last_completed"] else None
        task._reset_time = datetime.fromisoformat(data["reset_time"])
        return task