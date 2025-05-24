# handlers.py

import json
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime # Import datetime for date formatting

# Import utility functions
from utils import load_tasks, save_tasks, parse_datetime_input

# Define states for the expanded conversation
TITLE, DESCRIPTION, CATEGORY, DUE_DATE = range(4) # Now 4 states

# /start (remains unchanged)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message and lists available commands."""
    await update.message.reply_text(
        "سلام! 👋 من بات مدیریت تسک‌هام.\n"
        "دستورها:\n"
        "/add - برای اضافه کردن تسک جدید (عنوان و دسته‌بندی)\n"
        "/list - نمایش لیست تسک‌ها\n"
        "/delete [شماره] - حذف تسک با استفاده از شماره آن\n" # Adjusted delete to use number again
        "/cancel - برای لغو عملیات اضافه کردن تسک"
    )

# --- Conversation Handler for /add command ---

async def add_command_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation for adding a new task."""
    context.user_data['current_task_temp'] = {} # Use a temp key for conversation data
    await update.message.reply_text("عنوان تسک را وارد کنید:")
    return TITLE

async def ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks for the task description after getting the title."""
    title = update.message.text
    if not title:
        await update.message.reply_text("عنوان نمی‌تواند خالی باشد. لطفاً دوباره عنوان را وارد کنید:")
        return TITLE

    context.user_data['current_task_temp']['title'] = title
    await update.message.reply_text("توضیحات تسک را وارد کنید (اختیاری):")
    return DESCRIPTION

async def ask_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks for the task category after getting the description."""
    description = update.message.text
    context.user_data['current_task_temp']['description'] = description if description else "" # Description can be empty

    await update.message.reply_text("دسته‌بندی تسک را وارد کنید (مثال: کار، شخصی، مطالعه):")
    return CATEGORY

async def ask_due_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks for the due date after getting the category."""
    category = update.message.text
    if not category:
        await update.message.reply_text("دسته‌بندی نمی‌تواند خالی باشد. لطفاً دوباره دسته‌بندی را وارد کنید:")
        return CATEGORY

    context.user_data['current_task_temp']['category'] = category
    await update.message.reply_text("تاریخ و زمان سررسید را وارد کنید (اختیاری، مثال: 2025-06-01 20:00 یا 2025-06-01):")
    return DUE_DATE

async def save_full_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finalizes and saves the new task with all details."""
    due_date_str = update.message.text
    parsed_due_date = parse_datetime_input(due_date_str)

    # If user provided something but it's invalid
    if due_date_str and not parsed_due_date:
        await update.message.reply_text(
            "فرمت تاریخ و زمان سررسید نامعتبر است. لطفاً از فرمت 'YYYY-MM-DD HH:MM' یا 'YYYY-MM-DD' استفاده کنید یا خالی بگذارید:"
        )
        return DUE_DATE # Stay in the same state if input is invalid

    context.user_data['current_task_temp']['due_date'] = parsed_due_date.isoformat(timespec='minutes') if parsed_due_date else ""

    # Construct the task in the desired nested format
    new_task_data = {
        "task": {
            "title": context.user_data['current_task_temp']['title'],
            "description": context.user_data['current_task_temp']['description'],
            "category": context.user_data['current_task_temp']['category'],
            "due_date": context.user_data['current_task_temp']['due_date']
        }
    }

    # Load existing tasks, add the new one, and save
    tasks = load_tasks()
    tasks.append(new_task_data)
    save_tasks(tasks)

    await update.message.reply_text(
        f"✅ تسک '{new_task_data['task']['title']}' با دسته‌بندی '{new_task_data['task']['category']}' اضافه شد!"
    )

    # Clear user data for the current task
    del context.user_data['current_task_temp']
    return ConversationHandler.END # End the conversation

async def cancel_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the task addition process."""
    if 'current_task_temp' in context.user_data:
        del context.user_data['current_task_temp']
    await update.message.reply_text("عملیات اضافه کردن تسک لغو شد.")
    return ConversationHandler.END

# --- End of Conversation Handler ---

### `/list` Command (Adjusted)
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists all current tasks, displaying only their titles and categories."""
    tasks = load_tasks()

    if not tasks:
        await update.message.reply_text("📭 لیست تسک‌ها خالیه.")
        return

    message_parts = ["📝 لیست تسک‌ها:"]
    for i, item in enumerate(tasks):
        task_data = item.get('task') 
        if task_data and isinstance(task_data, dict):
            title = task_data.get('title', 'بدون عنوان')
            message_parts.append(f"{i+1}. {title}")
        else:
            message_parts.append(f"{i+1}. تسک نامعتبر")

    import re
    def escape_md(text: str) -> str:
        escape_chars = r'_*[]()~`>#+-=|{}.!\\'
        return re.sub(rf'([{re.escape(escape_chars)}])', r'\\\1', text)

    final_message_parts = [escape_md(part) for part in message_parts]

    await update.message.reply_markdown_v2("\n".join(final_message_parts))


# /delete (Adjusted to use index again as in your original simplified bot)
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes a task by its number."""
    try:
        index = int(context.args[0]) - 1 # Get index from 1-based user input
    except (IndexError, ValueError):
        await update.message.reply_text("❗️ لطفاً شماره تسک رو وارد کن. مثال: /delete 1")
        return

    tasks = load_tasks()

    if 0 <= index < len(tasks):
        removed_item = tasks.pop(index)
        save_tasks(tasks)

        # Try to get the title of the removed task for confirmation
        removed_title = "تسک نامشخص"
        if removed_item and isinstance(removed_item.get('task'), dict):
            removed_title = removed_item['task'].get('title', 'تسک نامشخص')

        await update.message.reply_text(f"🗑 حذف شد: {removed_title}")
    else:
        await update.message.reply_text("❗️ شماره معتبر نیست.")