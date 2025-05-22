import os
import json
import nest_asyncio
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# فعال‌سازی nest_asyncio برای جلوگیری از RuntimeError در Replit
nest_asyncio.apply()

# بارگذاری توکن
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# مسیر فایل دیتا
DATA_FILE = "data/tasks.json"

# اگر فایل دیتا وجود نداشت، بساز

# Ensure the directory exists and the file is initialized correctly at the start
# This part should be called once when your bot starts up, e.g., in your main() function
def ensure_data_file_initialized():
    # Create directory if it doesn't exist (if DATA_FILE includes a path)
    if os.path.dirname(DATA_FILE): # Check if DATA_FILE includes a directory
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    # If the file doesn't exist or is empty, initialize it with an empty JSON array
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
        print(f"Data file '{DATA_FILE}' initialized with empty list.")
    else:
        # Optional: Try to load to check if it's valid JSON
        try:
            with open(DATA_FILE, "r") as f:
                json.load(f)
            print(f"Data file '{DATA_FILE}' exists and is valid JSON.")
        except json.JSONDecodeError:
            print(f"Warning: Data file '{DATA_FILE}' exists but is not valid JSON. Re-initializing.")
            with open(DATA_FILE, "w") as f:
                json.dump([], f)
            print(f"Data file '{DATA_FILE}' re-initialized due to corruption.")


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋 من بات مدیریت تسک‌هام.\nدستورها:\n/add [تسک]\n/list\n/delete [شماره]")

# /add

# Your /add command handler
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        # You might want to call ensure_data_file_initialized() here or ensure it's called on bot startup
    except json.JSONDecodeError:
        await update.message.reply_text("خطا: فرمت فایل داده صحیح نیست. فایل احتمالا خراب شده است.")
        print("Error: JSON Decode Error, file might be empty or corrupt. Attempting to re-initialize.")
        # This means the content of the file was bad JSON.
        # You might want to try to re-initialize the file here or recover
        ensure_data_file_initialized() # Try to fix it on the fly
        await update.message.reply_text("فایل داده بازسازی شد. لطفاً دوباره تسک را اضافه کنید.")
    except Exception as e:
        await update.message.reply_text(f"خطای ناشناخته‌ای رخ داد: {e}")
        print(f"An unexpected error occurred: {e}")

# /list
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(DATA_FILE, "r") as f:
        tasks = json.load(f)
    if not tasks:
        await update.message.reply_text("📭 لیست تسک‌ها خالیه.")
        return
    message = "\n".join([f"{i+1}. {t['task']}" for i, t in enumerate(tasks)])
    await update.message.reply_text("📝 لیست تسک‌ها:\n" + message)

# /delete
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(context.args[0]) - 1
    except:
        await update.message.reply_text("❗️ لطفاً شماره تسک رو وارد کن.")
        return
    with open(DATA_FILE, "r+") as f:
        tasks = json.load(f)
        if 0 <= index < len(tasks):
            removed = tasks.pop(index)
            f.seek(0)
            json.dump(tasks, f, indent=2)
            f.truncate()
            await update.message.reply_text(f"🗑 حذف شد: {removed['task']}")
        else:
            await update.message.reply_text("❗️ شماره معتبر نیست.")

# اجرای بات
async def main():

    ensure_data_file_initialized()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("delete", delete))
    print("Bot is running...")
    await app.run_polling()

# اجرای امن برای Replit
if __name__ == "__main__":
    asyncio.run(main())
