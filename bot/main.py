# main.py

import os
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv

nest_asyncio.apply()

# Import functions and states
from handlers import (
    start,
    list_tasks,
    delete,
    add_command_entry,
    ask_description, # New state handler
    ask_category,
    ask_due_date, # New state handler
    save_full_task, # Renamed and updated final handler
    cancel_add_task,
    TITLE, DESCRIPTION, CATEGORY, DUE_DATE # Updated states
)
from utils import ensure_data_file_initialized

def main():
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    if not TOKEN:
        print("Error: TELEGRAM_TOKEN not found. Please set it in your .env file.")
        return

    ensure_data_file_initialized()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("delete", delete)) # Keep this if you have a delete command

    # Simplified Conversation Handler for adding a task
    add_task_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_command_entry)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_description)], # After title, ask description
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_category)], # After description, ask category
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_due_date)], # After category, ask due date
            DUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_full_task)], # After due date, save task
        },
        fallbacks=[CommandHandler("cancel", cancel_add_task)],
    )
    app.add_handler(add_task_conversation_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()