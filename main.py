from models.survivor import Survivor
from models.todo_task import TodoTask
from models.daily_task import DailyTask
from utils.data_manager import DataManager
from models.consumables import Food, Water, Medicine

def display_menu():
    print("\n=== Post-Apocalyptic RPG To-Do List ===")
    print("1. View Character Stats")
    print("2. Create New Task")
    print("3. View Tasks")
    print("4. Complete Task")
    print("5. Visit Marketplace")
    print("6. Delete Task")
    print("7. Settings")
    print("8. Save and Exit")
    return input("Choose an option (1-8): ")

def settings_menu(character, tasks):
    print("\n=== Settings ===")
    print(f"1. Change Character Name ({character._name})")
    print("2. Reset All Data")
    print("3. Back to Main Menu")
    
    choice = input("Choose an option (1-3): ")
    if choice == "1":
        new_name = input("Enter new character name: ")
        if new_name.strip():
            character._name = new_name.strip()
            print(f"Character name changed to: {character._name}")
        else:
            print("Name cannot be empty!")
    elif choice == "2":
        confirm = input("Are you sure you want to reset all data? This cannot be undone! (y/n): ").lower()
        if confirm == 'y':
            new_name = input("Enter new character name: ")
            if new_name.strip():
                character._name = new_name.strip() 
                character._level = 1
                character._xp = 0
                character._health = 30
                character._hunger = 100
                character._thirst = 100
                character._infection = 0
                tasks.clear()  # Clear all tasks
                print("All data has been reset to default values!")
            else:
                print("Reset cancelled - name cannot be empty!")
        else:
            print("Reset cancelled.")

def view_character_stats(character):
    print(f"\nCharacter Stats:")
    print(f"Name: {character._name}")
    print(f"Level: {character._level}")
    print(f"XP: {character._xp}/{character.calculate_xp_needed()}")
    print(f"Health: {character._health}/30")
    print(f"Hunger: {character._hunger}%")
    print(f"Thirst: {character._thirst}%")
    print(f"Infection: {character._infection}%")
    input("\nPress Enter to continue...")

def create_task(tasks):
    print("\nCreate New Task")
    
    # Task type validation
    while True:
        print("Task Types:")
        print("1. Todo")
        print("2. Habit")
        task_type = input("Choose task type (1 or 2): ").strip()
        if task_type in ["1", "2"]:
            break
        print("Error: Invalid task type! Please choose 1 for Todo or 2 for Habit.")
    
    # Title validation
    while True:
        title = input("Enter task title: ").strip()
        if title:  # Check if title is not empty
            break
        print("Error: Title is required!")
    
    description = input("Enter task description (optional): ").strip()
    
    if task_type == "1":
        while True:
            priority = input("Enter priority (low/medium/high) [default: low]: ").lower().strip()
            if not priority:  # If empty, set default to low
                priority = "low"
            if priority in ["low", "medium", "high"]:
                break
            print("Error: Priority must be low, medium, or high!")
            
        task = TodoTask(title, description, priority)
    else:
        task = DailyTask(title, description)  # Daily tasks are used for habits
    
    tasks.append(task)
    print("Task created successfully!")
    input("\nPress Enter to continue...")  # Added wait for input

def view_tasks(tasks, wait_for_input=True):
    if not tasks:
        print("\nNo tasks available.")
        if wait_for_input:
            input("\nPress Enter to continue...")  
        return
        
    print("\nCurrent Tasks:")
    for idx, task in enumerate(tasks):
        task_type = "Daily" if isinstance(task, DailyTask) else "Todo"
        priority = f" - Priority: {task._priority}" if isinstance(task, TodoTask) else ""
        status = "Completed" if task._completed else "Pending"
        print(f"{idx + 1}. [{task_type}] {task._title}{priority} - {status}")
    if wait_for_input:
        input("\nPress Enter to continue...")

def complete_task(character, tasks):
    view_tasks(tasks, wait_for_input=False)
    if not tasks:
        return
        
    try:
        task_idx = int(input("\nEnter task number to complete: ")) - 1
        if 0 <= task_idx < len(tasks):
            task = tasks[task_idx]
            success = True  # Default value
            if isinstance(task, DailyTask):
                success = input("Was the task successful? (y/n): ").lower() == 'y'
                reward = task.complete(success)
            else:
                reward = task.complete()
                
            if reward > 0:
                character._xp += reward
                print(f"Gained {reward} XP!")
                if character._xp >= character.calculate_xp_needed():
                    character.level_up()
                    print("Level Up!")
            else:
                character._health += reward
                print(f"Lost {abs(reward)} health points!")
                
            # Reduce stats after task completion
            character._hunger = max(0, character._hunger - 1)
            character._thirst = max(0, character._thirst - 1)
            if not success and isinstance(task, DailyTask):
                character._infection = min(100, character._infection + 1)
    except ValueError:
        print("Invalid input!")

def visit_marketplace(character):
    items = [
        Food("Food Ration", 10, 20),
        Water("Water Bottle", 8, 15),
        Medicine("Medkit", 15, 25)
    ]
    
    print("\nMarketplace:")
    for idx, item in enumerate(items):
        print(f"{idx + 1}. {item._name} - Cost: {item._cost} XP")
    
    try:
        choice = int(input("Choose item to buy (0 to exit): ")) - 1
        if 0 <= choice < len(items):
            item = items[choice]
            if character._xp >= item._cost:
                # Check if using the item would exceed maximum stats
                if isinstance(item, Food) and character._hunger + item._effect_value > 100:
                    print("You're not hungry enough to eat this!")
                elif isinstance(item, Water) and character._thirst + item._effect_value > 100:
                    print("You're not thirsty enough to drink this!")
                elif isinstance(item, Medicine) and character._infection - item._effect_value < 0:
                    print("You don't need medicine right now!")
                else:
                    character._xp -= item._cost
                    item.use(character)
                    print(f"Used {item._name} successfully!")
            else:
                print("Not enough XP!")
    except ValueError:
        print("Invalid input!")

def main():
    try:
        # Load game state or create new character
        game_state = DataManager.load_game_state()
        if game_state:
            # Initialize character and tasks from saved state
            character = Survivor(game_state["character"]["_name"])
            # Load all character stats from game_state
            character._level = game_state["character"]["_level"]
            character._xp = game_state["character"]["_xp"]
            character._health = game_state["character"]["_health"]
            character._hunger = game_state["character"]["_hunger"]
            character._thirst = game_state["character"]["_thirst"]
            character._infection = game_state["character"]["_infection"]
            
            # Load tasks from game_state
            tasks = []
            for task_data in game_state["tasks"]:
                if "priority" in task_data:
                    task = TodoTask(task_data["_title"], task_data["_description"], task_data.get("_priority", "low"))
                else:
                    task = DailyTask(task_data["_title"], task_data["_description"])
                task._completed = task_data["_completed"]
                tasks.append(task)
        else:
            name = input("Enter your character name: ")
            character = Survivor(name)
            tasks = []
        
        while True:
            choice = display_menu()
            
            if choice == "1":
                view_character_stats(character)
            elif choice == "2":
                create_task(tasks)
            elif choice == "3":
                view_tasks(tasks)
            elif choice == "4":
                complete_task(character, tasks)
            elif choice == "5":
                visit_marketplace(character)
            elif choice == "6":
                delete_task(tasks)
            elif choice == "7":
                settings_menu(character, tasks)
            elif choice == "8":
                break
            else:
                print("Invalid option!")
                
            # Check for game over condition
            if character._health <= 0:
                print("Game Over! Your character has died.")
                break
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Save game state before exit
        DataManager.save_game_state(character, tasks)
        print("Game saved. Goodbye!")

def delete_task(tasks):
    view_tasks(tasks, wait_for_input=False)
    if not tasks:
        return
        
    try:
        task_idx = int(input("\nEnter task number to delete: ")) - 1
        if 0 <= task_idx < len(tasks):
            task = tasks.pop(task_idx)
            print(f"Task '{task._title}' deleted successfully!")
        else:
            print("Invalid task number!")
    except ValueError:
        print("Invalid input!")

if __name__ == "__main__":
    main()