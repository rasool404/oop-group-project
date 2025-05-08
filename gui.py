import tkinter as tk
from tkinter import ttk, messagebox
from models.survivor import Survivor
from models.todo_task import TodoTask
from models.daily_task import DailyTask
from models.consumables import Food, Water, Medicine
from utils.data_manager import DataManager

class RPGGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Post-Apocalyptic RPG To-Do List")
        self.root.geometry("800x600")
        
        # Load game state
        game_state = DataManager.load_game_state()
        if game_state:
            self.character = Survivor(game_state["character"]["_name"])
            self.character._level = game_state["character"]["_level"]
            self.character._xp = game_state["character"]["_xp"]
            self.character._health = game_state["character"]["_health"]
            self.character._hunger = game_state["character"]["_hunger"]
            self.character._thirst = game_state["character"]["_thirst"]
            self.character._infection = game_state["character"]["_infection"]
            
            self.tasks = []
            for task_data in game_state["tasks"]:
                if "priority" in task_data:
                    task = TodoTask(task_data["_title"], task_data["_description"], task_data.get("_priority", "low"))
                else:
                    task = DailyTask(task_data["_title"], task_data["_description"])
                task._completed = task_data["_completed"]
                self.tasks.append(task)
        else:
            self.character = None
            self.tasks = []
            self.show_new_character_dialog()
            
        self.create_widgets()
        
    def show_new_character_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Character")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        
        tk.Label(dialog, text="Enter character name:").pack(pady=10)
        name_entry = tk.Entry(dialog)
        name_entry.pack(pady=5)
        
        def create_character():
            name = name_entry.get().strip()
            if name:
                self.character = Survivor(name)
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Name cannot be empty!")
                
        tk.Button(dialog, text="Create", command=create_character).pack(pady=10)
        dialog.grab_set()
        
    def create_widgets(self):
        # Character Stats Frame
        stats_frame = ttk.LabelFrame(self.root, text="Character Stats")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.stats_labels = {}
        stats = [
            ("Name", "_name"),
            ("Level", "_level"),
            ("XP", "_xp"),
            ("Health", "_health"),
            ("Hunger", "_hunger"),
            ("Thirst", "_thirst"),
            ("Infection", "_infection")
        ]
        
        for i, (label, attr) in enumerate(stats):
            tk.Label(stats_frame, text=f"{label}:").grid(row=i//3, column=(i%3)*2, padx=5, pady=2)
            self.stats_labels[attr] = tk.Label(stats_frame, text="")
            self.stats_labels[attr].grid(row=i//3, column=(i%3)*2+1, padx=5, pady=2)
            
        # Tasks Frame
        tasks_frame = ttk.LabelFrame(self.root, text="Tasks")
        tasks_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Task List
        self.task_list = ttk.Treeview(tasks_frame, columns=("Type", "Title", "Status"), show="headings")
        self.task_list.heading("Type", text="Type")
        self.task_list.heading("Title", text="Title")
        self.task_list.heading("Status", text="Status")
        self.task_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="New Task", command=self.create_task_dialog).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Complete Task", command=self.complete_task_dialog).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Visit Marketplace", command=self.show_marketplace).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Save & Exit", command=self.save_and_exit).pack(side="right", padx=5)
        
        self.update_display()
        
    def update_display(self):
        # Update stats
        for attr, label in self.stats_labels.items():
            value = getattr(self.character, attr)
            if attr == "_xp":
                value = f"{value}/{self.character.calculate_xp_needed()}"
            elif attr == "_health":
                value = f"{value}/30"
            elif attr in ["_hunger", "_thirst", "_infection"]:
                value = f"{value}%"
            label.config(text=str(value))
            
        # Update task list
        for item in self.task_list.get_children():
            self.task_list.delete(item)
            
        for task in self.tasks:
            task_type = "Daily" if isinstance(task, DailyTask) else "Todo"
            status = "Completed" if task._completed else "Pending"
            self.task_list.insert("", "end", values=(task_type, task._title, status))
            
    def create_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Task")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        tk.Label(dialog, text="Task Type:").pack(pady=5)
        task_type = tk.StringVar(value="1")
        ttk.Radiobutton(dialog, text="Todo", variable=task_type, value="1").pack()
        ttk.Radiobutton(dialog, text="Habit", variable=task_type, value="2").pack()
        
        tk.Label(dialog, text="Title:").pack(pady=5)
        title_entry = tk.Entry(dialog)
        title_entry.pack()
        
        tk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = tk.Entry(dialog)
        desc_entry.pack()
        
        priority_var = tk.StringVar(value="low")
        priority_frame = ttk.LabelFrame(dialog, text="Priority (Todo only)")
        priority_frame.pack(pady=10)
        ttk.Radiobutton(priority_frame, text="Low", variable=priority_var, value="low").pack(side="left")
        ttk.Radiobutton(priority_frame, text="Medium", variable=priority_var, value="medium").pack(side="left")
        ttk.Radiobutton(priority_frame, text="high", variable=priority_var, value="high").pack(side="left")
        
        def create_task():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Title is required!")
                return
                
            desc = desc_entry.get().strip()
            if task_type.get() == "1":
                task = TodoTask(title, desc, priority_var.get())
            else:
                task = DailyTask(title, desc)
                
            self.tasks.append(task)
            self.update_display()
            dialog.destroy()
            
        ttk.Button(dialog, text="Create", command=create_task).pack(pady=10)
        dialog.grab_set()
        
    def complete_task_dialog(self):
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to complete!")
            return
            
        idx = self.task_list.index(selection[0])
        task = self.tasks[idx]
        
        if task._completed:
            messagebox.showinfo("Info", "This task is already completed!")
            return
            
        if isinstance(task, DailyTask):
            if messagebox.askyesno("Success?", "Was the task successful?"):
                status = task.complete(True)
                reward = task.calculate_reward()
            else:
                status = task.complete(False)
                reward = -5
        else:
            status = task.complete()
            reward = task.calculate_reward()
            
        if status == "completed":
            if reward > 0:
                self.character._xp += reward
                messagebox.showinfo("Success", f"Gained {reward} XP!")
                if self.character._xp >= self.character.calculate_xp_needed():
                    self.character.level_up()
                    messagebox.showinfo("Level Up!", "You've reached the next level!")
            else:
                self.character._health += reward
                messagebox.showinfo("Failure", f"Lost {abs(reward)} health points!")
                
            self.character._hunger = max(0, self.character._hunger - 1)
            self.character._thirst = max(0, self.character._thirst - 1)
            if not success and isinstance(task, DailyTask):
                self.character._infection = min(100, self.character._infection + 1)
                
        self.update_display()
        
    def show_marketplace(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Marketplace")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        items = [
            Food("Food Ration", 10, 20),
            Water("Water Bottle", 8, 15),
            Medicine("Medkit", 15, 25)
        ]
        
        for item in items:
            frame = ttk.Frame(dialog)
            frame.pack(fill="x", padx=5, pady=2)
            tk.Label(frame, text=f"{item._name} - {item._cost} XP").pack(side="left")
            
            def make_buy_command(item):
                def buy_item():
                    if self.character._xp >= item._cost:
                        if isinstance(item, Food) and self.character._hunger + item._effect_value > 100:
                            messagebox.showwarning("Warning", "You're not hungry enough!")
                        elif isinstance(item, Water) and self.character._thirst + item._effect_value > 100:
                            messagebox.showwarning("Warning", "You're not thirsty enough!")
                        elif isinstance(item, Medicine) and self.character._infection - item._effect_value < 0:
                            messagebox.showwarning("Warning", "You don't need medicine!")
                        else:
                            self.character._xp -= item._cost
                            item.use(self.character)
                            messagebox.showinfo("Success", f"Used {item._name} successfully!")
                            self.update_display()
                            dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Not enough XP!")
                return buy_item
                
            ttk.Button(frame, text="Buy", command=make_buy_command(item)).pack(side="right")
            
        dialog.grab_set()
        
    def save_and_exit(self):
        try:
            DataManager.save_game_state(self.character, self.tasks)
            messagebox.showinfo("Success", "Game saved successfully!")
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save game: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RPGGUI(root)
    root.mainloop()