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
        self.root.geometry("850x650")
        
        # Initialize stats_labels dictionary before any potential usage
        self.stats_labels = {}
        
        # Configure style
        self.configure_styles()
        
       
        
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
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg="#2D2D30")
    
        content_frame = ttk.Frame(dialog, padding=20, style="TFrame")
        content_frame.pack(expand=True, fill="both")
    
        ttk.Label(content_frame, text="Enter character name:", font=("Arial", 11)).pack(pady=(0,10))
        name_entry = ttk.Entry(content_frame, font=("Arial", 10), width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
    
        def create_character():
            name = name_entry.get().strip()
            if name:
                self.character = Survivor(name)
                if not self.tasks:
                    self.tasks = []
                dialog.destroy()
                # Move update_display() call after create_widgets() in __init__
            else:
                messagebox.showerror("Error", "Name cannot be empty!", parent=dialog)
        
        button_frame = ttk.Frame(content_frame, style="TFrame")
        button_frame.pack(pady=(15,0))
        ttk.Button(button_frame, text="Create", command=create_character, style="TButton").pack()
        
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.root.quit() if self.character is None else dialog.destroy())
        self.root.wait_window(dialog)
        
        if self.character is None:
            if self.root.winfo_exists():
                 self.root.quit()

   
        
    def create_widgets(self):
        # Character Stats Frame
        stats_frame = ttk.LabelFrame(self.root, text="Character Stats", style="Custom.TLabelframe")
        stats_frame.pack(fill="x", padx=10, pady=(10,5))
        
        self.stats_labels = {}
        stats_data = [
            ("Name", "_name"),
            ("Level", "_level"),
            ("XP", "_xp"),
            ("Health", "_health"),
            ("Hunger", "_hunger"),
            ("Thirst", "_thirst"),
            ("Infection", "_infection")
        ]
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
    
        for i, (label_text, attr) in enumerate(stats_data):
            item_frame = ttk.Frame(stats_frame, style="StatsItem.TFrame")
            item_frame.grid(row=i//3, column=i%3, padx=10, pady=5, sticky="ew")
            
            text_label = ttk.Label(item_frame, text=f"{label_text}:", 
                                   font=("Arial", 10, "bold"),
                                   background="#252526",
                                   foreground="#A0A0A0")
            text_label.pack(side="left", padx=(0, 5))
                    
            self.stats_labels[attr] = ttk.Label(item_frame,
                                                text="",
                                                font=("Arial", 10),
                                                background="#252526",
                                                foreground="#F0F0F0")
            self.stats_labels[attr].pack(side="left", padx=(0, 5))
        
        # Tasks Frame
        tasks_frame = ttk.LabelFrame(self.root, text="Tasks", style="Custom.TLabelframe")
        tasks_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Task List with Priority Column
        self.task_list = ttk.Treeview(tasks_frame,
                                     columns=("Type", "Title", "Priority", "Status"),
                                     show="headings",
                                     style="Custom.Treeview")
                                     
        self.task_list.heading("Type", text="Type")
        self.task_list.heading("Title", text="Title")
        self.task_list.heading("Priority", text="Priority")  # New Priority Column
        self.task_list.heading("Status", text="Status")
    
        # Add a scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(tasks_frame, orient="vertical", command=self.task_list.yview, style="TScrollbar")
        self.task_list.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.task_list.pack(fill="both", expand=True, padx=(5,0), pady=5)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(self.root, style="TFrame")
        buttons_frame.pack(fill="x", padx=10, pady=(5,10))
        
        # Left side buttons
        left_buttons_frame = ttk.Frame(buttons_frame, style="TFrame")
        left_buttons_frame.pack(side="left")
        
        button_texts_left = ["New Task", "Complete Task", "Edit Task", "Delete Task", "Marketplace"]
        commands_left = [self.create_task_dialog, self.complete_task_dialog, self.edit_task_dialog, self.delete_task_dialog, self.show_marketplace]
    
        for text, command in zip(button_texts_left, commands_left):
            ttk.Button(left_buttons_frame, text=text, command=command, style="TButton").pack(side="left", padx=5)
        
        # Right side buttons
        right_buttons_frame = ttk.Frame(buttons_frame, style="TFrame")
        right_buttons_frame.pack(side="right")
        
        button_texts_right = ["Settings", "Save & Exit"]
        commands_right = [self.show_settings, self.save_and_exit]
    
        for text, command in zip(button_texts_right, commands_right):
             ttk.Button(right_buttons_frame, text=text, command=command, style="TButton").pack(side="right", padx=5)
        
        self.update_display()

    def delete_task_dialog(self):
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to delete!")
            return
            
        idx = self.task_list.index(selection[0])
        task = self.tasks[idx]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task: {task._title}?"):
            self.tasks.pop(idx)
            self.update_display()
            messagebox.showinfo("Success", "Task deleted successfully!")
            
    def edit_task_dialog(self):
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to edit!")
            return
            
        idx = self.task_list.index(selection[0])
        task_to_edit = self.tasks[idx]

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Task")
        dialog.geometry("400x300") # Adjusted size
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg="#2D2D30")

        content_frame = ttk.Frame(dialog, padding=20, style="TFrame")
        content_frame.pack(expand=True, fill="both")

        ttk.Label(content_frame, text="Title:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        title_entry = ttk.Entry(content_frame, width=40, font=("Arial", 10))
        title_entry.insert(0, task_to_edit._title)
        title_entry.grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(content_frame, text="Description:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        desc_entry = ttk.Entry(content_frame, width=40, font=("Arial", 10))
        desc_entry.insert(0, task_to_edit._description)
        desc_entry.grid(row=1, column=1, pady=5, sticky="ew")
        
        priority_label = ttk.Label(content_frame, text="Priority (for Todo):", font=("Arial", 10))
        priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(content_frame, textvariable=priority_var, values=["low", "medium", "high"], state="readonly", font=("Arial", 10))

        if isinstance(task_to_edit, TodoTask):
            priority_label.grid(row=2, column=0, sticky="w", pady=5)
            priority_var.set(task_to_edit._priority)
            priority_combo.grid(row=2, column=1, pady=5, sticky="ew")
        
        content_frame.columnconfigure(1, weight=1)

        def save_changes():
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showerror("Error", "Title is required!")
                return
                
            task_to_edit._title = new_title  # Use task_to_edit instead of task
            task_to_edit._description = desc_entry.get().strip()
            
            if isinstance(task_to_edit, TodoTask):
                task_to_edit._priority = priority_var.get()
                
            self.update_display()
            dialog.destroy()
            messagebox.showinfo("Success", "Task updated successfully!")
            
        ttk.Button(dialog, text="Save Changes", command=save_changes).pack(pady=10)
        dialog.grab_set()
        
    def show_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        # Change Character Name
        name_frame = ttk.LabelFrame(dialog, text="Change Character Name")
        name_frame.pack(fill="x", padx=10, pady=5)
        
        name_entry = tk.Entry(name_frame)
        name_entry.insert(0, self.character._name)
        name_entry.pack(padx=5, pady=5)
        
        def change_name():
            new_name = name_entry.get().strip()
            if new_name:
                self.character._name = new_name
                self.update_display()
                messagebox.showinfo("Success", "Character name updated!")
            else:
                messagebox.showerror("Error", "Name cannot be empty!")
                
        ttk.Button(name_frame, text="Change Name", command=change_name).pack(pady=5)
        
        # Reset All Data
        reset_frame = ttk.LabelFrame(dialog, text="Reset All Data")
        reset_frame.pack(fill="x", padx=10, pady=5)
        
        def reset_data():
            if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all data? This cannot be undone!"):
                new_name = name_entry.get().strip()
                if new_name:
                    self.character._name = new_name
                    self.character._level = 1
                    self.character._xp = 0
                    self.character._health = 30
                    self.character._hunger = 100
                    self.character._thirst = 100
                    self.character._infection = 0
                    self.tasks.clear()
                    self.update_display()
                    dialog.destroy()
                    messagebox.showinfo("Success", "All data has been reset!")
                else:
                    messagebox.showerror("Error", "Name cannot be empty!")
                    
        ttk.Button(reset_frame, text="Reset All Data", command=reset_data).pack(pady=5)
        
        dialog.grab_set()
        
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
            priority = task._priority if isinstance(task, TodoTask) else "-"  # Show priority for TodoTask, "-" for DailyTask
            self.task_list.insert("", "end", values=(task_type, task._title, priority, status))
            
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
        title_entry = ttk.Entry(dialog)
        title_entry.pack()
        
        tk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = ttk.Entry(dialog)
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
            
        success = True  # Initialize success variable
        if isinstance(task, DailyTask):
            success = messagebox.askyesno("Success?", "Was the task successful?")
            status = task.complete(success)
            reward = task.calculate_reward() if success else -5
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
                
            # Reduce stats after task completion
            self.character._hunger = max(0, self.character._hunger - 1)
            self.character._thirst = max(0, self.character._thirst - 1)
            if not success and isinstance(task, DailyTask):
                self.character._infection = min(100, self.character._infection + 1)
                
        self.update_display()
        
    def show_marketplace(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Marketplace")
        dialog.geometry("450x350") # Adjusted size
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg="#2D2D30")

        content_frame = ttk.Frame(dialog, padding=15, style="TFrame")
        content_frame.pack(expand=True, fill="both")

        ttk.Label(content_frame, text="Available Items:", font=("Arial", 12, "bold"), foreground="#00AACC").pack(pady=(0,10))
        
        items = [
            Food("Food Ration", 10, 20),
            Water("Water Bottle", 8, 15),
            Medicine("Medkit", 15, 25)
        ]
        
        for item in items:
            item_frame = ttk.Frame(content_frame, style="TFrame", relief="solid", borderwidth=1)
            item_frame.pack(fill="x", padx=5, pady=5, ipady=5) # Added ipady for internal padding
            
            # Use ttk.Label for consistent styling
            ttk.Label(item_frame, text=f"{item._name} - Cost: {item._cost} XP", font=("Arial", 10)).pack(side="left", padx=10)
            
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
                
            ttk.Button(item_frame, text="Buy", command=make_buy_command(item)).pack(side="right")
            
        close_button_frame = ttk.Frame(content_frame, style="TFrame")
        close_button_frame.pack(pady=(15,0))
        ttk.Button(close_button_frame, text="Close", command=dialog.destroy, style="TButton").pack()

    def save_and_exit(self):
        try:
            DataManager.save_game_state(self.character, self.tasks)
            messagebox.showinfo("Success", "Game saved successfully!")
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save game: {str(e)}")

    def configure_styles(self):
        self.root.configure(bg="#2D2D30") # Dark background for the root window

        style = ttk.Style()
        style.theme_use("clam") # 'clam' theme is often a good base for customization

        # General widget styling
        style.configure("TFrame", background="#2D2D30")
        style.configure("StatsItem.TFrame", background="#252526") # New style for stat items
        style.configure("TLabel", background="#2D2D30", foreground="#F0F0F0", font=("Arial", 10))
        style.configure("Custom.TLabel", 
                       font=("Arial", 10),
                       background="#2b2b2b",
                       foreground="white")
                       
        style.configure("Header.TLabel", 
                       font=("Arial", 12, "bold"),
                       background="#2b2b2b",
                       foreground="white")
                       
        style.configure("Stats.TLabel", 
                       font=("Arial", 10),
                       padding=5,
                       background="#2b2b2b",
                       foreground="white")
                       
        style.configure("Custom.TButton", 
                       font=("Arial", 9),
                       padding=5)
                       
        # Configure frames
        style.configure("Custom.TLabelframe", 
                       background="#2b2b2b",
                       foreground="white",
                       padding=10)
                       
        style.configure("Custom.TLabelframe.Label", 
                       font=("Arial", 11, "bold"),
                       foreground="white",
                       background="#2b2b2b")
                       
        # Configure Treeview
        style.configure("Custom.Treeview",
                       background="#3b3b3b",
                       foreground="white",
                       fieldbackground="#3b3b3b")
                       
        style.configure("Custom.Treeview.Heading",
                       background="#4a4a4a",
                       foreground="white",
                       font=("Arial", 10, "bold"))
                       
        # Configure the root window background
        self.root.configure(bg="#1e1e1e")

if __name__ == "__main__":
    root = tk.Tk()
    app = RPGGUI(root)
    root.mainloop()