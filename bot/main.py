import os
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
        from dotenv import load_dotenv

        # Apply nest_asyncio for Replit compatibility
        nest_asyncio.apply()

        # Import functions from other files
        from handlers import (
            start,
            list_tasks,
            delete,
            add_command_entry, # New entry point for conversation
            ask_description,
            ask_category,
            ask_due_date,
            ask_reminder_time,
            save_task,
            cancel_add_task, # New cancel handler
            TITLE, DESCRIPTION, CATEGORY, DUE_DATE, REMINDER_TIME # States
        )
        from utils import ensure_data_file_initialized # Import only the function, DATA_FILE is used internally now


        def main():
            # Load environment variables
            load_dotenv()
            TOKEN = os.getenv("TELEGRAM_TOKEN")

            if not TOKEN:
                print("Error: TELEGRAM_TOKEN not found. Please set it in your .env file.")
                return

            # Ensure the data file and its directory are initialized
            ensure_data_file_initialized()

            # Build the application
            app = ApplicationBuilder().token(TOKEN).build()

            # Register command handlers
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("list", list_tasks))
            app.add_handler(CommandHandler("delete", delete))

            # Conversation Handler for adding a task
            add_task_conversation_handler = ConversationHandler(
                entry_points=[CommandHandler("add", add_command_entry)],
                states={
                    TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_description)],
                    DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_category)],
                    CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_due_date)],
                    DUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_reminder_time)],
                    REMINDER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_task)],
                },
                fallbacks=[CommandHandler("cancel", cancel_add_task)],
            )
            app.add_handler(add_task_conversation_handler)

            print("Bot is running...")
            app.run_polling()


        if __name__ == "__main__":
            main()