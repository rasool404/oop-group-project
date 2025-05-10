import tkinter as tk
from tkinter import ttk, messagebox
import json # Moved import to top for DataManager
import os   # Moved import to top for DataManager
# Assuming your models are in these paths
from models.survivor import Survivor
from models.todo_task import TodoTask 
from models.daily_task import DailyTask
from models.consumables import Food, Water, Medicine
# from utils.data_manager import DataManager # DataManager is now part of this file for the example
import datetime

# --- DataManager Class (Modified for Character-Specific Saves) ---
class DataManager:
    SAVE_FILE_TEMPLATE = "{character_name}_rpg_todo_save.json"
    SAVE_DIRECTORY = "save_data" # Optional: subdirectory for saves

    @staticmethod
    def _ensure_save_directory_exists():
        """Ensures the save directory exists."""
        if DataManager.SAVE_DIRECTORY and not os.path.exists(DataManager.SAVE_DIRECTORY):
            try:
                os.makedirs(DataManager.SAVE_DIRECTORY)
            except OSError as e:
                print(f"Error creating save directory {DataManager.SAVE_DIRECTORY}: {e}")
                # Fallback to current directory if subdir creation fails
                return "" 
        return DataManager.SAVE_DIRECTORY

    @staticmethod
    def get_save_file_path(character_name):
        """Generates a safe and unique file path for a character's save data."""
        if not character_name: # Should not happen if character object is validated
            return None
        # Basic sanitization for filename
        safe_character_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in character_name).strip().replace(' ', '_')
        if not safe_character_name:
            safe_character_name = "default_character" # Fallback for empty/invalid names after sanitization
        
        filename = DataManager.SAVE_FILE_TEMPLATE.format(character_name=safe_character_name)
        
        save_dir = DataManager._ensure_save_directory_exists()
        if save_dir:
            return os.path.join(save_dir, filename)
        return filename # Save in current directory if no subdir or subdir creation failed


    @staticmethod
    def save_game_state(character, tasks):
        """Saves the game state for the given character."""
        if character is None or not character._name:
            messagebox.showerror("Save Error", "Cannot save game: Character data is missing or name is invalid.")
            return False # Indicate failure

        file_path = DataManager.get_save_file_path(character._name)
        if not file_path:
            messagebox.showerror("Save Error", "Cannot save game: Invalid character name for file path.")
            return False

        game_state = {
            "character": character.__dict__,
            "tasks": [task.__dict__ for task in tasks]
        }
        try:
            with open(file_path, "w") as f:
                json.dump(game_state, f, indent=4)
            print(f"Game state saved to {file_path}")
            return True # Indicate success
        except IOError as e:
            messagebox.showerror("Save Error", f"Failed to save game to {file_path}: {e}")
            return False
        except Exception as e: # Catch any other unexpected errors during save
            messagebox.showerror("Save Error", f"An unexpected error occurred while saving: {e}")
            return False


    @staticmethod
    def load_game_state(character_name):
        """Loads the game state for the given character name."""
        if not character_name:
            return None

        file_path = DataManager.get_save_file_path(character_name)
        if not file_path or not os.path.exists(file_path):
            return None # File doesn't exist for this character

        try:
            with open(file_path, "r") as f:
                game_state = json.load(f)
            print(f"Game state loaded from {file_path}")
            return game_state
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showwarning("Load Warning", f"Could not load save data for '{character_name}'. File might be corrupted or inaccessible.\nError: {e}")
            return None
        except Exception as e: # Catch any other unexpected errors during load
            messagebox.showerror("Load Error", f"An unexpected error occurred while loading '{character_name}': {e}")
            return None

class RPGGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Post-Apocalyptic RPG To-Do List")
        self.root.geometry("850x700")
        
        # Initialize core attributes
        self.stats_labels = {}
        self.tasks = [] 
        self.character = None # Will be set by show_character_login_create_dialog
        
        self.configure_styles()
        
        # Create all UI widgets (like self.task_list) before any potential update_display calls
        self.create_widgets() 
        
        # Handle character loading or creation process
        self.show_character_login_create_dialog()
        
        # If no character was loaded or created (e.g., user closed the initial dialog), quit.
        if self.character is None:
            if self.root.winfo_exists(): # Check if root window still exists
                 self.root.quit()

    def configure_styles(self):
        # Post-apocalyptic light theme colors (global for access in dialogs if needed)
        global MAIN_BG, DARKER_BG, ACCENT, TEXT_COLOR, SECONDARY_TEXT, HIGHLIGHT
        MAIN_BG = "#E6D5AC"
        DARKER_BG = "#C4B594"
        ACCENT = "#8B4513"
        TEXT_COLOR = "#2F4F4F"
        SECONDARY_TEXT = "#556B2F"
        HIGHLIGHT = "#CD853F"
        
        self.root.configure(bg=MAIN_BG)
        style = ttk.Style()
        style.theme_use('clam')
    
        style.configure(".", 
                      background=MAIN_BG,
                      foreground=TEXT_COLOR,
                      fieldbackground=DARKER_BG,
                      troughcolor=DARKER_BG,
                      selectbackground=ACCENT,
                      selectforeground="#FFFFFF")
    
        style.configure("TFrame", background=MAIN_BG)
        style.configure("Card.TFrame", background=DARKER_BG, relief="solid", borderwidth=1)
        
        style.configure("TLabel", 
                      background=MAIN_BG,
                      foreground=TEXT_COLOR,
                      font=("Segoe UI", 10))
        
        style.configure("Header.TLabel",
                      font=("Segoe UI", 12, "bold"),
                      foreground=ACCENT)
        
        style.configure("DetailHeader.TLabel",
                      font=("Segoe UI", 11, "bold"),
                      foreground=SECONDARY_TEXT,
                      background=DARKER_BG)

        style.configure("DetailValue.TLabel",
                      font=("Segoe UI", 10),
                      foreground=TEXT_COLOR,
                      background=DARKER_BG)
        
        style.configure("TButton",
                      padding=10,
                      background=ACCENT,
                      foreground="#FFFFFF",
                      font=("Segoe UI", 10))
        
        style.map("TButton",
                background=[('active', HIGHLIGHT), ('pressed', ACCENT)],
                foreground=[('active', "#FFFFFF"), ('pressed', "#FFFFFF")])
    
        style.configure("Treeview",
                      background=DARKER_BG,
                      foreground=TEXT_COLOR,
                      fieldbackground=DARKER_BG,
                      font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading",
                      background=MAIN_BG,
                      foreground=TEXT_COLOR,
                      font=("Segoe UI", 10, "bold"))
        
        style.map("Treeview",
                background=[('selected', ACCENT)],
                foreground=[('selected', "#FFFFFF")])
    
        style.configure("TEntry",
                      padding=5,
                      selectbackground=ACCENT)
    
        style.configure("TLabelframe",
                      background=MAIN_BG,
                      foreground=TEXT_COLOR)
        
        style.configure("TLabelframe.Label",
                      background=MAIN_BG,
                      foreground=ACCENT,
                      font=("Segoe UI", 11, "bold"))

        style.configure("Custom.TLabelframe.Label",
                      background=MAIN_BG,
                      foreground=ACCENT,
                      font=("Segoe UI", 11, "bold"))

        style.configure("StatsItem.TFrame", background=DARKER_BG)
        style.configure("Highlight.TFrame", background="#8B4513") 
        style.configure("Inner.TFrame", background="#E6D5AC") 
        style.configure("Stats.TLabel", background="#E6D5AC", foreground="#2F4F4F")
        
        style.configure("DetailText.TText", 
                        background=DARKER_BG,
                        foreground=TEXT_COLOR,
                        font=("Segoe UI", 10),
                        relief="solid",
                        borderwidth=1,
                        padx=5,
                        pady=5)

    def show_character_login_create_dialog(self):
        """Handles character login (loading) or creation."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Login or Create Character")
        dialog.geometry("380x220") # Slightly larger for more text
        dialog.transient(self.root)
        dialog.grab_set() # Make modal
        dialog.configure(bg=self.root.cget('bg'))
    
        content_frame = ttk.Frame(dialog, padding=20, style="TFrame")
        content_frame.pack(expand=True, fill="both")
    
        ttk.Label(content_frame, text="Enter Character Name:", font=("Segoe UI", 11, "bold")).pack(pady=(0,10))
        name_entry = ttk.Entry(content_frame, font=("Segoe UI", 10), width=35)
        name_entry.pack(pady=5)
        name_entry.focus()

        status_label = ttk.Label(content_frame, text="", font=("Segoe UI", 9), style="TLabel")
        status_label.pack(pady=(5,0))
    
        def attempt_login_or_create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Character name cannot be empty!", parent=dialog)
                return

            status_label.config(text=f"Checking for '{name}'...")
            dialog.update_idletasks() # Ensure label updates

            game_state = DataManager.load_game_state(name)
            
            if game_state:
                if messagebox.askyesno("Character Found", f"Character '{name}' found. Load this character's data?", parent=dialog):
                    try:
                        # Populate self.character
                        char_data = game_state["character"]
                        self.character = Survivor(char_data["_name"]) # Use name from save file for consistency
                        self.character._level = char_data.get("_level", 1)
                        self.character._xp = char_data.get("_xp", 0)
                        self.character._health = char_data.get("_health", Survivor.MAX_HEALTH)
                        self.character._hunger = char_data.get("_hunger", 0)
                        self.character._thirst = char_data.get("_thirst", 0)
                        self.character._infection = char_data.get("_infection", 0)
                        
                        # Populate self.tasks
                        self.tasks.clear() # Clear any default/previous tasks
                        for task_data in game_state.get("tasks", []):
                            task_attributes = {
                                "_deadline": task_data.get("_deadline", "Not set"),
                                "_scheduled_start_time": task_data.get("_scheduled_start_time", "Not set"),
                                "_scheduled_end_time": task_data.get("_scheduled_end_time", "Not set"),
                                "_is_recurring": task_data.get("_is_recurring", "No"),
                                "_base_xp_reward": task_data.get("_base_xp_reward", 0),
                                "_base_gold_reward": task_data.get("_base_gold_reward", 0),
                                "_base_item_rewards": task_data.get("_base_item_rewards", []),
                                "_early_bonus_condition": task_data.get("_early_bonus_condition", "N/A"),
                                "_early_bonus_xp": task_data.get("_early_bonus_xp", 0),
                                "_sub_tasks": task_data.get("_sub_tasks", [])
                            }
                            if "priority" in task_data: # TodoTask
                                task = TodoTask(task_data["_title"], task_data["_description"], task_data.get("_priority", "low"))
                            else: # DailyTask
                                task = DailyTask(task_data["_title"], task_data["_description"])
                            task._completed = task_data.get("_completed", False)
                            for attr_name, attr_value in task_attributes.items():
                                setattr(task, attr_name, attr_value)
                            self.tasks.append(task)
                        
                        self.update_display()
                        dialog.destroy()
                    except KeyError as e:
                        messagebox.showerror("Load Error", f"Save file for '{name}' is corrupted or has missing data: {e}. Please create a new character or try another.", parent=dialog)
                        self.character = None # Ensure character is not partially loaded
                        self.tasks.clear()
                        status_label.config(text="Error loading. Try again.")
                    except Exception as e: # Catch any other unexpected errors during parsing
                        messagebox.showerror("Load Error", f"An unexpected error occurred parsing save data for '{name}': {e}", parent=dialog)
                        self.character = None
                        self.tasks.clear()
                        status_label.config(text="Error loading. Try again.")

                else: # User chose not to load existing character
                    status_label.config(text="Load cancelled. Enter a different name or create.")
                    # Keep dialog open for user to enter a different name or proceed to create
            else: # No save file found, proceed to creation
                if messagebox.askyesno("Create New Character", f"No save data found for '{name}'. Create a new character with this name?", parent=dialog):
                    self.character = Survivor(name)
                    self.tasks = [] # Ensure fresh task list for new character
                    self.update_display() # Update display with new character's default stats
                    dialog.destroy()
                else:
                    status_label.config(text="Creation cancelled. Try another name.")
        
        button_frame = ttk.Frame(content_frame, style="TFrame")
        button_frame.pack(pady=(15,0))
        ttk.Button(button_frame, text="Login / Create", command=attempt_login_or_create, style="TButton").pack()
        
        # Handle dialog close button: if no character is set by then, the main app will quit.
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy) 
        self.root.wait_window(dialog) # Block execution until this dialog is closed

    def create_widgets(self):
        # Character Stats Frame
        stats_frame = ttk.LabelFrame(self.root, text="Character Stats", style="Custom.TLabelframe")
        stats_frame.pack(fill="x", padx=10, pady=(10,5))
        
        stats_data = [
            ("Name", "_name"), ("Level", "_level"), ("XP", "_xp"),
            ("Health", "_health"), ("Hunger", "_hunger"), ("Thirst", "_thirst"),
            ("Infection", "_infection")
        ]
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
    
        for i, (label_text, attr) in enumerate(stats_data):
            item_frame = ttk.Frame(stats_frame, style="TFrame") 
            item_frame.grid(row=i//3, column=i%3, padx=10, pady=5, sticky="ew")
            
            highlight_frame = ttk.Frame(item_frame, style="Highlight.TFrame")
            highlight_frame.pack(fill="x", padx=2, pady=2)
            
            inner_frame = ttk.Frame(highlight_frame, style="Inner.TFrame")
            inner_frame.pack(fill="x", padx=1, pady=1)
            
            text_label = ttk.Label(inner_frame, text=f"{label_text}:", font=("Segoe UI", 10, "bold"), style="Stats.TLabel")
            text_label.pack(side="left", padx=(5, 2))
                    
            self.stats_labels[attr] = ttk.Label(inner_frame, text="-", font=("Segoe UI", 10), style="Stats.TLabel") # Default to "-"
            self.stats_labels[attr].pack(side="left", padx=(2, 5), fill="x", expand=True)
        
        # Tasks Frame
        tasks_frame = ttk.LabelFrame(self.root, text="Tasks", style="Custom.TLabelframe")
        tasks_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.task_list = ttk.Treeview(tasks_frame,
                                     columns=("Type", "Title", "Priority", "Status"),
                                     show="headings",
                                     style="Treeview") 
                                     
        self.task_list.heading("Type", text="Type")
        self.task_list.heading("Title", text="Title")
        self.task_list.heading("Priority", text="Priority")
        self.task_list.heading("Status", text="Status")

        self.task_list.column("Type", width=80, anchor="w", minwidth=60)
        self.task_list.column("Title", width=300, anchor="w", minwidth=150)
        self.task_list.column("Priority", width=80, anchor="center", minwidth=60)
        self.task_list.column("Status", width=100, anchor="center", minwidth=80)
    
        scrollbar = ttk.Scrollbar(tasks_frame, orient="vertical", command=self.task_list.yview) 
        self.task_list.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.task_list.pack(fill="both", expand=True, padx=(5,0), pady=5)

        self.task_list.bind("<Double-1>", self.on_task_double_click)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(self.root, style="TFrame")
        buttons_frame.pack(fill="x", padx=10, pady=(5,10))
        
        left_buttons_frame = ttk.Frame(buttons_frame, style="TFrame")
        left_buttons_frame.pack(side="left")
        
        button_texts_left = ["New Task", "View Details", "Complete Task", "Edit Task", "Delete Task", "Marketplace"]
        commands_left = [self.create_task_dialog, self.open_selected_task_details, self.complete_task_dialog, 
                         self.edit_task_dialog, self.delete_task_dialog, self.show_marketplace]
    
        for text, command in zip(button_texts_left, commands_left):
            ttk.Button(left_buttons_frame, text=text, command=command, style="TButton").pack(side="left", padx=3)
        
        right_buttons_frame = ttk.Frame(buttons_frame, style="TFrame")
        right_buttons_frame.pack(side="right")
        
        button_texts_right = ["Settings", "Save & Exit"]
        commands_right = [self.show_settings, self.save_and_exit]
    
        for text, command in zip(button_texts_right, commands_right):
             ttk.Button(right_buttons_frame, text=text, command=command, style="TButton").pack(side="right", padx=3)
        
        # Initial display update will be handled after character is loaded/created
        # self.update_display() # Removed from here, called by login/create dialog logic

    def on_task_double_click(self, event):
        if not self.character: return # Don't do anything if no character is active
        self.open_selected_task_details()

    def open_selected_task_details(self):
        if not self.character: return
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("No Task Selected", "Please select a task to view its details.", parent=self.root)
            return
        
        # Find task by title from selection (more robust if task list can be reordered)
        # For simplicity, still using index if tasks are always in self.tasks order
        try:
            idx = self.task_list.index(selection[0])
            if 0 <= idx < len(self.tasks):
                task = self.tasks[idx]
                self.show_task_details_dialog(task)
            else:
                messagebox.showerror("Error", "Could not find the selected task (index out of bounds).", parent=self.root)
        except ValueError:
             messagebox.showerror("Error", "Could not find the selected task in the list.", parent=self.root)


    def show_task_details_dialog(self, task):
        if not self.character: return
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Task Details: {task._title}")
        dialog.geometry("550x650")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.root.cget('bg')) 

        main_frame = ttk.Frame(dialog, padding=15, style="TFrame")
        main_frame.pack(expand=True, fill="both")

        canvas = tk.Canvas(main_frame, bg=self.root.cget('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame") 

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        info_frame = ttk.LabelFrame(scrollable_frame, text="Task Information", style="TLabelframe")
        info_frame.pack(fill="x", padx=10, pady=10)
        info_frame.columnconfigure(1, weight=1)

        row_idx = 0
        details_to_show = [
            ("Title:", task._title),
            ("Type:", "Daily Task" if isinstance(task, DailyTask) else "To-Do Task"),
            ("Status:", "Completed" if task._completed else "Pending"),
        ]
        if isinstance(task, TodoTask):
            details_to_show.append(("Priority:", getattr(task, '_priority', 'N/A')))

        for label, value in details_to_show:
            ttk.Label(info_frame, text=label, style="DetailHeader.TLabel").grid(row=row_idx, column=0, sticky="nw", padx=5, pady=3)
            ttk.Label(info_frame, text=value, style="DetailValue.TLabel", wraplength=350).grid(row=row_idx, column=1, sticky="new", padx=5, pady=3)
            row_idx += 1

        desc_frame = ttk.LabelFrame(scrollable_frame, text="Description", style="TLabelframe")
        desc_frame.pack(fill="x", padx=10, pady=10)

        desc_text_widget = tk.Text(desc_frame, wrap=tk.WORD, height=6, 
                                   font=("Segoe UI", 10), relief="flat",
                                   bg=DARKER_BG, fg=TEXT_COLOR, 
                                   padx=5, pady=5) 
        desc_text_widget.insert(tk.END, task._description if task._description else "No description provided.")
        desc_text_widget.config(state=tk.DISABLED) 
        desc_text_widget.pack(fill="x", expand=True, padx=5, pady=5)
        
        time_frame = ttk.LabelFrame(scrollable_frame, text="Time & Scheduling", style="TLabelframe")
        time_frame.pack(fill="x", padx=10, pady=10)
        time_frame.columnconfigure(1, weight=1)

        time_details = [
            ("Deadline:", getattr(task, '_deadline', "Not set")),
            ("Scheduled Start:", getattr(task, '_scheduled_start_time', "Not set")),
            ("Scheduled End:", getattr(task, '_scheduled_end_time', "Not set")),
            ("Recurring:", getattr(task, '_is_recurring', "No")),
        ]
        row_idx = 0
        for label, value in time_details:
            ttk.Label(time_frame, text=label, style="DetailHeader.TLabel").grid(row=row_idx, column=0, sticky="nw", padx=5, pady=3)
            ttk.Label(time_frame, text=value, style="DetailValue.TLabel").grid(row=row_idx, column=1, sticky="new", padx=5, pady=3)
            row_idx +=1

        rewards_frame = ttk.LabelFrame(scrollable_frame, text="Rewards & Incentives", style="TLabelframe")
        rewards_frame.pack(fill="x", padx=10, pady=10)
        rewards_frame.columnconfigure(1, weight=1)

        base_xp = getattr(task, '_base_xp_reward', 0)
        # Ensure calculate_reward exists and is callable before using it as a fallback
        if base_xp == 0 and hasattr(task, 'calculate_reward') and callable(getattr(task, 'calculate_reward')) and not task._completed:
            base_xp = task.calculate_reward()

        reward_details = [
            ("Base XP:", str(base_xp)),
            ("Base Gold:", str(getattr(task, '_base_gold_reward', "0"))),
            ("Base Items:", ", ".join(getattr(task, '_base_item_rewards', [])) or "None"),
            ("Early Bonus Condition:", getattr(task, '_early_bonus_condition', "N/A")),
            ("Early Bonus XP:", str(getattr(task, '_early_bonus_xp', "0"))),
        ]
        row_idx = 0
        for label, value in reward_details:
            ttk.Label(rewards_frame, text=label, style="DetailHeader.TLabel").grid(row=row_idx, column=0, sticky="nw", padx=5, pady=3)
            ttk.Label(rewards_frame, text=value, style="DetailValue.TLabel", wraplength=350).grid(row=row_idx, column=1, sticky="new", padx=5, pady=3)
            row_idx += 1
            
        sub_tasks = getattr(task, '_sub_tasks', [])
        if sub_tasks:
            sub_tasks_frame = ttk.LabelFrame(scrollable_frame, text="Sub-Tasks / Checklist", style="TLabelframe")
            sub_tasks_frame.pack(fill="x", padx=10, pady=10)
            for i, sub_task_desc in enumerate(sub_tasks):
                # Assuming sub_task_desc is a string. If it's a dict with 'completed' status:
                # sub_status = "✓" if sub_task_desc.get('completed') else "☐"
                # ttk.Label(sub_tasks_frame, text=f"{sub_status} {sub_task_desc.get('description', '')}"...
                ttk.Label(sub_tasks_frame, text=f"- {sub_task_desc}", style="DetailValue.TLabel", wraplength=450).pack(anchor="w", padx=10, pady=2)

        close_button = ttk.Button(scrollable_frame, text="Close", command=dialog.destroy, style="TButton")
        close_button.pack(pady=15)

        scrollable_frame.update_idletasks() 
        canvas.config(scrollregion=canvas.bbox("all"))

    def delete_task_dialog(self):
        if not self.character: return
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to delete!", parent=self.root)
            return
            
        idx = self.task_list.index(selection[0])
        if not (0 <= idx < len(self.tasks)):
            messagebox.showerror("Error", "Invalid task selection.", parent=self.root)
            return

        task = self.tasks[idx]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task: {task._title}?", parent=self.root):
            self.tasks.pop(idx)
            self.update_display()
            messagebox.showinfo("Success", "Task deleted successfully!", parent=self.root)
            
    def edit_task_dialog(self):
        if not self.character: return
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to edit!", parent=self.root)
            return
            
        idx = self.task_list.index(selection[0])
        if not (0 <= idx < len(self.tasks)):
            messagebox.showerror("Error", "Invalid task selection.", parent=self.root)
            return

        task_to_edit = self.tasks[idx]

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Task")
        dialog.geometry("450x350") 
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.root.cget('bg'))

        content_frame = ttk.Frame(dialog, padding=20, style="Card.TFrame")
        content_frame.pack(expand=True, fill="both", padx=10, pady=10)

        ttk.Label(content_frame, text="Title:", style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        title_entry = ttk.Entry(content_frame, width=40, font=("Segoe UI", 10))
        title_entry.insert(0, task_to_edit._title)
        title_entry.grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(content_frame, text="Description:", style="Header.TLabel").grid(row=1, column=0, sticky="nw", pady=5)
        desc_text = tk.Text(content_frame, width=40, height=5, font=("Segoe UI", 10), wrap=tk.WORD,
                             bg=DARKER_BG, fg=TEXT_COLOR, relief="solid", borderwidth=1)
        desc_text.insert("1.0", task_to_edit._description)
        desc_text.grid(row=1, column=1, pady=5, sticky="ew")
        
        priority_label = ttk.Label(content_frame, text="Priority (Todo):", style="Header.TLabel")
        priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(content_frame, textvariable=priority_var, values=["low", "medium", "high"], state="readonly", font=("Segoe UI", 10))

        if isinstance(task_to_edit, TodoTask):
            priority_label.grid(row=2, column=0, sticky="w", pady=5)
            priority_var.set(getattr(task_to_edit, '_priority', 'low')) 
            priority_combo.grid(row=2, column=1, pady=5, sticky="ew")
        
        content_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(content_frame, style="TFrame") 
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)

        def save_changes():
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showerror("Error", "Title is required!", parent=dialog)
                return
                
            task_to_edit._title = new_title
            task_to_edit._description = desc_text.get("1.0", tk.END).strip()
            
            if isinstance(task_to_edit, TodoTask):
                task_to_edit._priority = priority_var.get()
                
            self.update_display()
            dialog.destroy()
            messagebox.showinfo("Success", "Task updated successfully!", parent=self.root)
            
        ttk.Button(button_frame, text="Save Changes", command=save_changes, style="TButton").pack()
        
    def show_settings(self):
        if not self.character: 
            messagebox.showinfo("No Character", "No character is currently active.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("400x350") # Increased height for new option
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.root.cget('bg'))
        
        main_settings_frame = ttk.Frame(dialog, padding=10, style="TFrame")
        main_settings_frame.pack(expand=True, fill="both")

        name_frame = ttk.LabelFrame(main_settings_frame, text="Change Character Name", style="TLabelframe")
        name_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(name_frame, text="Current Name:", style="TLabel").pack(side="left", padx=(5,0), pady=5)
        current_name_label = ttk.Label(name_frame, text=self.character._name, style="TLabel", font=("Segoe UI", 10, "bold"))
        current_name_label.pack(side="left", padx=(0,10), pady=5)

        ttk.Label(name_frame, text="New Name:", style="TLabel").pack(side="left", padx=(15,0), pady=5)
        name_entry = ttk.Entry(name_frame, font=("Segoe UI", 10))
        name_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        def change_name_action():
            old_name = self.character._name
            new_name = name_entry.get().strip()

            if not new_name:
                messagebox.showerror("Error", "New name cannot be empty!", parent=dialog)
                return
            if new_name == old_name:
                messagebox.showinfo("Info", "New name is the same as the current name.", parent=dialog)
                return

            # Check if a save file for the new name already exists
            if os.path.exists(DataManager.get_save_file_path(new_name)):
                if not messagebox.askyesno("Overwrite Warning", 
                                           f"A character named '{new_name}' already has saved data. Overwrite it with '{old_name}'s data?",
                                           parent=dialog):
                    return # User cancelled overwrite

            # Proceed with name change
            self.character._name = new_name
            # Save under new name (this also effectively renames the save file on next save)
            if DataManager.save_game_state(self.character, self.tasks):
                # Optionally, delete the old save file
                old_file_path = DataManager.get_save_file_path(old_name)
                if old_file_path and os.path.exists(old_file_path) and old_file_path != DataManager.get_save_file_path(new_name):
                    try:
                        os.remove(old_file_path)
                        print(f"Old save file '{old_file_path}' deleted.")
                    except OSError as e:
                        print(f"Could not delete old save file '{old_file_path}': {e}")
                
                self.update_display() # Update character name in UI
                current_name_label.config(text=new_name) # Update label in settings dialog
                name_entry.delete(0, tk.END) # Clear entry
                messagebox.showinfo("Success", f"Character name changed to '{new_name}'. Game saved.", parent=dialog)
            else:
                # Revert name if save failed
                self.character._name = old_name 
                messagebox.showerror("Error", "Failed to save game with new name. Name change reverted.", parent=dialog)
                
        ttk.Button(name_frame, text="Change & Save Name", command=change_name_action, style="TButton").pack(pady=10, side="bottom", fill="x")
        
        reset_frame = ttk.LabelFrame(main_settings_frame, text="Reset Current Character Data", style="TLabelframe")
        reset_frame.pack(fill="x", padx=10, pady=10)
        
        def reset_current_character_data():
            if not self.character: return
            if messagebox.askyesno("Confirm Reset", 
                                   f"Are you sure you want to reset all data for '{self.character._name}'? This character will be reset to Level 1 with default stats and no tasks. This cannot be undone!", 
                                   parent=dialog):
                
                char_name_before_reset = self.character._name # Keep the name
                self.character = Survivor(char_name_before_reset) # Re-initialize with the same name
                self.tasks.clear()
                
                if DataManager.save_game_state(self.character, self.tasks): # Save the reset state
                    self.update_display()
                    messagebox.showinfo("Success", f"All data for '{char_name_before_reset}' has been reset and saved.", parent=dialog)
                    dialog.destroy() # Close settings after successful reset
                else:
                    messagebox.showerror("Error", "Failed to save the reset data. Please try again.", parent=dialog)
                    # Potentially reload the character from file if save failed to avoid inconsistent state
                    # For now, we assume if save fails, the in-memory reset is what user sees until next load/save attempt.

        ttk.Button(reset_frame, text=f"Reset '{self.character._name}' Data", command=reset_current_character_data, style="TButton").pack(pady=10)
        
    def update_display(self):
        if not self.character: 
            # Set UI to a default "no character loaded" state
            for attr, label in self.stats_labels.items():
                label.config(text="-")
            if hasattr(self, 'task_list'): # Check if task_list exists
                for item in self.task_list.get_children():
                    self.task_list.delete(item)
            return

        # Update stats if character exists
        for attr, label in self.stats_labels.items():
            value = getattr(self.character, attr, "-") 
            if attr == "_name": # Ensure name is directly from character object
                 value = self.character._name
            elif attr == "_xp":
                value = f"{value}/{self.character.calculate_xp_needed()}"
            elif attr == "_health":
                value = f"{value}/{Survivor.MAX_HEALTH}" 
            elif attr in ["_hunger", "_thirst", "_infection"]:
                value = f"{value}%"
            label.config(text=str(value))
            
        # Update task list
        if hasattr(self, 'task_list'):
            for item in self.task_list.get_children():
                self.task_list.delete(item)
            for task in self.tasks:
                task_type = "Daily" if isinstance(task, DailyTask) else "Todo"
                status = "Completed" if task._completed else "Pending"
                priority = getattr(task, '_priority', '-') if isinstance(task, TodoTask) else "-"
                self.task_list.insert("", "end", values=(task_type, task._title, priority, status))
            
    def create_task_dialog(self):
        if not self.character: 
            messagebox.showinfo("No Character", "Please load or create a character before adding tasks.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Task")
        dialog.geometry("500x450") 
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.root.cget('bg'))
        
        content_frame = ttk.Frame(dialog, padding=20, style="Card.TFrame")
        content_frame.pack(expand=True, fill="both", padx=15, pady=15)
        content_frame.columnconfigure(1, weight=1)
        
        ttk.Label(content_frame, text="Task Type:", style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=(0,10))
        task_type_var = tk.StringVar(value="Todo") 
        radio_frame = ttk.Frame(content_frame, style="TFrame")
        radio_frame.grid(row=0, column=1, sticky="ew", pady=(0,10))
        ttk.Radiobutton(radio_frame, text="Todo", variable=task_type_var, value="Todo").pack(side="left", padx=10)
        ttk.Radiobutton(radio_frame, text="Daily", variable=task_type_var, value="Daily").pack(side="left", padx=10)
        
        ttk.Label(content_frame, text="Title:", style="Header.TLabel").grid(row=1, column=0, sticky="w", pady=(5,5))
        title_entry = ttk.Entry(content_frame, font=("Segoe UI", 10), width=40)
        title_entry.grid(row=1, column=1, sticky="ew", pady=(5,5))
        
        ttk.Label(content_frame, text="Description:", style="Header.TLabel").grid(row=2, column=0, sticky="nw", pady=(5,5))
        desc_text = tk.Text(content_frame, height=5, width=40, wrap=tk.WORD, font=("Segoe UI", 10),
                            bg=DARKER_BG, fg=TEXT_COLOR, relief="solid", borderwidth=1, padx=5, pady=5)
        desc_text.grid(row=2, column=1, sticky="ew", pady=(5,15))
        
        priority_frame = ttk.LabelFrame(content_frame, text="Priority (Todo only)", style="TLabelframe")
        priority_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5,15))
        priority_var = tk.StringVar(value="low")
        
        radio_container = ttk.Frame(priority_frame, style="TFrame") 
        radio_container.pack(pady=5)
        priorities = [("Low", "low"), ("Medium", "medium"), ("High", "high")]
        for text, value in priorities:
            ttk.Radiobutton(radio_container, text=text, variable=priority_var, value=value).pack(side="left", padx=10, expand=True)
        
        time_fields_frame = ttk.LabelFrame(content_frame, text="Time & Rewards (Optional)", style="TLabelframe")
        time_fields_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(5,15))
        time_fields_frame.columnconfigure(1, weight=1)

        ttk.Label(time_fields_frame, text="Deadline (YYYY-MM-DD HH:MM):", style="TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        deadline_entry = ttk.Entry(time_fields_frame, font=("Segoe UI", 10))
        deadline_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(time_fields_frame, text="Base XP Reward:", style="TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        base_xp_entry = ttk.Entry(time_fields_frame, font=("Segoe UI", 10))
        base_xp_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        button_frame = ttk.Frame(content_frame, style="TFrame")
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10,0))
        
        def create_task_action():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Title is required!", parent=dialog)
                return
                
            desc = desc_text.get("1.0", tk.END).strip()
            task_class = TodoTask if task_type_var.get() == "Todo" else DailyTask
            
            if task_class == TodoTask:
                new_task = TodoTask(title, desc, priority_var.get())
            else:
                new_task = DailyTask(title, desc)

            setattr(new_task, '_deadline', deadline_entry.get().strip() or "Not set")
            try:
                base_xp_val = int(base_xp_entry.get().strip()) if base_xp_entry.get().strip() else 0
            except ValueError:
                base_xp_val = 0 
            setattr(new_task, '_base_xp_reward', base_xp_val)
            # Initialize other placeholder attributes
            for attr_key in ['_scheduled_start_time', '_scheduled_end_time', '_is_recurring', 
                             '_early_bonus_condition']:
                setattr(new_task, attr_key, "Not set" if "condition" in attr_key else "No") # Sensible defaults
            for attr_key_num in ['_base_gold_reward', '_early_bonus_xp']:
                setattr(new_task, attr_key_num, 0)
            setattr(new_task, '_base_item_rewards', [])
            setattr(new_task, '_sub_tasks', [])


            self.tasks.append(new_task)
            self.update_display()
            dialog.destroy()
            messagebox.showinfo("Success", "Task created successfully!", parent=self.root)

        create_btn = ttk.Button(button_frame, text="Create Task", command=create_task_action, style="TButton")
        create_btn.pack(pady=5)
        
    def complete_task_dialog(self):
        if not self.character: return
        selection = self.task_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to complete!", parent=self.root)
            return
            
        idx = self.task_list.index(selection[0])
        if not (0 <= idx < len(self.tasks)):
            messagebox.showerror("Error", "Invalid task selection.", parent=self.root)
            return
        task = self.tasks[idx]
        
        if task._completed:
            messagebox.showinfo("Info", "This task is already completed!", parent=self.root)
            return
            
        success = True 
        xp_reward = 0
        health_change = 0

        if isinstance(task, DailyTask):
            success = messagebox.askyesno("Success?", "Was the daily task successful today?", parent=self.root)
            status_message = task.complete(success) 
            xp_reward = task.calculate_reward() if success else 0 
            if not success:
                 health_change = -5 # Example penalty
        else: # TodoTask
            status_message = task.complete() # Assumes this sets task._completed = True
            xp_reward = task.calculate_reward()
                
        if status_message == "completed": 
            if xp_reward > 0:
                self.character._xp += xp_reward
                messagebox.showinfo("Success", f"Task '{task._title}' completed! Gained {xp_reward} XP.", parent=self.root)
                if self.character._xp >= self.character.calculate_xp_needed():
                    self.character.level_up() 
                    messagebox.showinfo("Level Up!", f"You've reached Level {self.character._level}!", parent=self.root)
            
            if health_change != 0:
                self.character._health = max(0, self.character._health + health_change)
                if health_change < 0:
                    messagebox.showwarning("Penalty", f"Lost {abs(health_change)} health due to task failure.", parent=self.root)

            self.character._hunger = max(0, self.character._hunger + 5) 
            self.character._thirst = max(0, self.character._thirst + 5) 
            
            if not success and isinstance(task, DailyTask): 
                self.character._infection = min(100, self.character._infection + 2) 
                
            if self.character._health <= 0:
                messagebox.showerror("Game Over", "Your health reached 0. You have perished.", parent=self.root)
                # Consider a more graceful game over, e.g., disabling buttons, showing a game over screen
                self.root.quit() 
        # else: # If complete() could return other statuses like "already_completed"
            # messagebox.showinfo("Info", status_message, parent=self.root) 
                
        self.update_display()
        
    def show_marketplace(self):
        if not self.character: 
            messagebox.showinfo("No Character", "Please load or create a character to access the marketplace.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Marketplace")
        dialog.geometry("450x400") 
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.root.cget('bg'))

        content_frame = ttk.Frame(dialog, padding=15, style="Card.TFrame")
        content_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        ttk.Label(content_frame, text="Available Items:", style="Header.TLabel", foreground=ACCENT).pack(pady=(0,10))
        
        items = [
            Food("Food Ration", 10, 20),  
            Water("Purified Water", 8, 25), 
            Medicine("Basic Medkit", 20, 30) 
        ]
        
        items_frame = ttk.Frame(content_frame, style="TFrame")
        items_frame.pack(fill="x", expand=True)

        for item in items:
            item_card_frame = ttk.Frame(items_frame, style="Card.TFrame", relief="solid", borderwidth=1)
            item_card_frame.pack(fill="x", padx=5, pady=5, ipady=5)
            
            item_info = f"{item._name} (Cost: {item._cost} XP)"
            if isinstance(item, Food): item_info += f" - Hunger: -{item._effect_value}"
            elif isinstance(item, Water): item_info += f" - Thirst: -{item._effect_value}"
            elif isinstance(item, Medicine): item_info += f" - Health: +{item._effect_value}"

            ttk.Label(item_card_frame, text=item_info, style="DetailValue.TLabel", background=DARKER_BG).pack(side="left", padx=10)
            
            def make_buy_command(current_item): 
                def buy_item_action():
                    if not self.character: return # Should be caught by initial check

                    if self.character._xp >= current_item._cost:
                        can_use = True
                        # Using current_item directly for type checking and effect application
                        if isinstance(current_item, Food):
                            if self.character._hunger >= 100:
                                messagebox.showwarning("Full", "You're not hungry enough to eat this.", parent=dialog)
                                can_use = False
                            else: current_item.use(self.character) # Use method handles stat update
                        elif isinstance(current_item, Water):
                            if self.character._thirst >= 100:
                                messagebox.showwarning("Full", "You're not thirsty enough to drink this.", parent=dialog)
                                can_use = False
                            else: current_item.use(self.character)
                        elif isinstance(current_item, Medicine):
                            if self.character._health >= Survivor.MAX_HEALTH: 
                                messagebox.showwarning("Healthy", "Your health is already full.", parent=dialog)
                                can_use = False
                            else: current_item.use(self.character)
                        
                        if can_use:
                            self.character._xp -= current_item._cost
                            messagebox.showinfo("Purchase Successful", f"You bought and used {current_item._name}.", parent=dialog)
                            self.update_display()
                        
                    else:
                        messagebox.showerror("Error", "Not enough XP to buy this item!", parent=dialog)
                return buy_item_action
                
            ttk.Button(item_card_frame, text="Buy & Use", command=make_buy_command(item), style="TButton").pack(side="right", padx=10)
            
        close_button_frame = ttk.Frame(content_frame, style="TFrame")
        close_button_frame.pack(pady=(15,0))
        ttk.Button(close_button_frame, text="Close Marketplace", command=dialog.destroy, style="TButton").pack()

    def save_and_exit(self):
        if not self.character:
            if messagebox.askyesno("Exit?", "No active character. Exit anyway?", parent=self.root):
                self.root.quit()
            return

        if DataManager.save_game_state(self.character, self.tasks):
            messagebox.showinfo("Success", f"Game saved for {self.character._name}!", parent=self.root)
        else:
            # Save_game_state already shows an error, but we can add a generic one here if needed
            messagebox.showwarning("Save Issue", "There was an issue saving the game. Check previous messages.", parent=self.root)
            # Ask if user still wants to exit if save failed
            if not messagebox.askyesno("Exit Confirmation", "Failed to save game. Exit without saving?", parent=self.root):
                return 
        self.root.quit()

# --- Dummy Model Classes (Ensure these match your actual model structure) ---
class Survivor:
    MAX_HEALTH = 30 
    def __init__(self, name):
        self._name = name
        self._level = 1
        self._xp = 0
        self._health = Survivor.MAX_HEALTH # Use class attribute
        self._hunger = 0
        self._thirst = 0
        self._infection = 0
    def calculate_xp_needed(self): return self._level * 100 
    def level_up(self): 
        self._level += 1
        # XP needed for next level increases, current XP might reset or carry over based on game design
        # For simplicity, let's say XP resets to 0 towards the new goal.
        # self._xp = self._xp - self.calculate_xp_needed() # If XP carries over
        self._xp = 0 # If XP resets
        self._health = self.MAX_HEALTH 
        # Potentially increase MAX_HEALTH or other stats
        print(f"{self._name} leveled up to Level {self._level}!")

class Task: # Base Task class
    def __init__(self, title, description):
        self._title = title
        self._description = description
        self._completed = False
        # Initialize all potential time-based/reward attributes for consistent __dict__
        self._deadline = "Not set"
        self._scheduled_start_time = "Not set"
        self._scheduled_end_time = "Not set"
        self._is_recurring = "No"
        self._base_xp_reward = 0
        self._base_gold_reward = 0
        self._base_item_rewards = []
        self._early_bonus_condition = "N/A"
        self._early_bonus_xp = 0
        self._sub_tasks = []


    def complete(self): # Basic complete, can be overridden
        if not self._completed:
            self._completed = True
            return "completed"
        return "already_completed" # Or handle as info

    def calculate_reward(self): # Base reward, can be overridden
        # This should ideally use self._base_xp_reward if set, or a default
        return getattr(self, '_base_xp_reward', 10) if getattr(self, '_base_xp_reward', 0) > 0 else 10


class TodoTask(Task):
    def __init__(self, title, description, priority="low"):
        super().__init__(title, description)
        self._priority = priority
        if self._base_xp_reward == 0: # Set default based on priority if not specified
             self._base_xp_reward = {"low": 10, "medium": 15, "high": 20}.get(self._priority, 10)


    def calculate_reward(self):
        # Uses base_xp_reward possibly modified by priority, or a default logic
        base_reward = super().calculate_reward() # This gets self._base_xp_reward or default 10
        priority_multiplier = {"low": 1, "medium": 1.2, "high": 1.5} # Adjusted multipliers
        # If self._base_xp_reward was already set considering priority, this might double-dip.
        # Let's assume self._base_xp_reward is the fundamental reward.
        # Priority could be an additional small bonus on top or influence this base.
        # For now, let's assume self._base_xp_reward IS the reward.
        return int(base_reward * priority_multiplier.get(self._priority, 1)) if self._base_xp_reward == 0 else self._base_xp_reward


class DailyTask(Task):
    def __init__(self, title, description):
        super().__init__(title, description)
        if self._base_xp_reward == 0: # Default XP for daily
            self._base_xp_reward = 15

    def complete(self, success=True): # Daily tasks can succeed or fail
        if success:
            # Daily tasks might reset completion status daily, not just mark as permanently done
            # For now, behaves like TodoTask completion for simplicity of RPGGUI logic
            self._completed = True 
            return "completed"
        else:
            # Handle failure state if needed (e.g., penalties applied elsewhere)
            return "failed" 
    # calculate_reward uses the inherited method, which refers to self._base_xp_reward


class Consumable:
    def __init__(self, name, cost, effect_value):
        self._name = name
        self._cost = cost 
        self._effect_value = effect_value
    def use(self, character): 
        """Applies the consumable's effect to the character."""
        pass 

class Food(Consumable):
    def use(self, character):
        character._hunger = min(0, character._hunger - self._effect_value)
class Water(Consumable):
    def use(self, character):
        character._thirst = min(0, character._thirst - self._effect_value)
class Medicine(Consumable):
    def use(self, character): 
        character._health = min(Survivor.MAX_HEALTH, character._health + self._effect_value)
        # Could also reduce infection:
        # character._infection = max(0, character._infection - self._effect_value // 2) 


if __name__ == '__main__':
    root = tk.Tk()
    app = RPGGUI(root)
    root.mainloop()
