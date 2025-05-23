import json
from telegram import Update
from telegram.ext import ContextTypes

# Import DATA_FILE and ensure_data_file_initialized from utils
from utils import DATA_FILE, ensure_data_file_initialized

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message and lists available commands."""
    await update.message.reply_text("سلام! 👋 من بات مدیریت تسک‌هام.\nدستورها:\n/add [تسک]\n/list\n/delete [شماره]")

# /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds a new task to the list."""
    print("Received /add command")
    task = " ".join(context.args)
    if not task:
        await update.message.reply_text("❗️ لطفاً متن تسک رو وارد کن.")
        print("No task provided.")
        return

    print(f"Task received: {task}")

    tasks = [] # Initialize tasks as an empty list by default

    try:
        with open(DATA_FILE, "r+") as f:
            print("Opened data file for reading and writing.")
            # Attempt to load existing tasks
            file_content = f.read()
            if file_content: # Only try to load if file is not empty
                f.seek(0) # Reset pointer after reading content (if we read it)
                tasks = json.loads(file_content) # Use json.loads for string
                print("Loaded tasks from file.")
            else:
                print("Data file was empty, starting with an empty task list.")
                tasks = [] # Ensure it's an empty list if file was truly empty

            # Add the new task
            tasks.append({"task": task})

            # Write the updated list back to the file
            f.seek(0) # Go to the beginning of the file
            json.dump(tasks, f, indent=2)
            f.truncate() # Remove any leftover content if the new data is smaller
            print("Task saved successfully.")
            await update.message.reply_text(f"✅ تسک اضافه شد: {task}")

    except FileNotFoundError:
        await update.message.reply_text("خطا: فایل داده پیدا نشد. لطفاً مطمئن شوید bot/data/tasks.json وجود دارد.")
        print(f"Error: DATA_FILE '{DATA_FILE}' not found.")
    except json.JSONDecodeError:
        await update.message.reply_text("خطا: فرمت فایل داده صحیح نیست. فایل احتمالا خراب شده است.")
        print("Error: JSON Decode Error, file might be empty or corrupt. Attempting to re-initialize.")
        ensure_data_file_initialized() # Try to fix it on the fly
        await update.message.reply_text("فایل داده بازسازی شد. لطفاً دوباره تسک را اضافه کنید.")
    except Exception as e:
        await update.message.reply_text(f"خطای ناشناخته‌ای رخ داد: {e}")
        print(f"An unexpected error occurred: {e}")

# /list
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists all current tasks."""
    try:
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = [] # If file not found or corrupt, treat as empty

    if not tasks:
        await update.message.reply_text("📭 لیست تسک‌ها خالیه.")
        return

    # Format tasks for display
    message = "\n".join([f"{i+1}. {t['task']}" for i, t in enumerate(tasks)])
    await update.message.reply_text("📝 لیست تسک‌ها:\n" + message)

# /delete
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes a task by its number."""
    try:
        # Get the task index from command arguments (e.g., /delete 1)
        index = int(context.args[0]) - 1 
    except (IndexError, ValueError):
        await update.message.reply_text("❗️ لطفاً شماره تسک رو وارد کن.")
        return

    try:
        with open(DATA_FILE, "r+") as f:
            tasks = json.load(f) # Load all tasks
            if 0 <= index < len(tasks):
                removed = tasks.pop(index) # Remove the task
                f.seek(0) # Go to the beginning of the file
                json.dump(tasks, f, indent=2) # Write updated tasks
                f.truncate() # Trim any leftover data
                await update.message.reply_text(f"🗑 حذف شد: {removed['task']}")
            else:
                await update.message.reply_text("❗️ شماره معتبر نیست.")
    except (FileNotFoundError, json.JSONDecodeError):
        await update.message.reply_text("خطا: لیست تسک‌ها خالی است یا فایل داده خراب است.")
    except Exception as e:
        await update.message.reply_text(f"خطای ناشناخته‌ای رخ داد: {e}")
        print(f"An unexpected error occurred in delete: {e}")