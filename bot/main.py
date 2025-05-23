import os
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv

# Apply nest_asyncio for Replit compatibility
nest_asyncio.apply()

# Import functions from other files
from handlers import start, add, list_tasks, delete
from utils import ensure_data_file_initialized, DATA_FILE # Import DATA_FILE from utils


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
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("delete", delete))

    print("Bot is running...")
    # Run the bot (this is an async function, so it needs to be awaited in an async context)
    # The asyncio.run(main()) at the bottom handles this
    app.run_polling() # In newer versions, run_polling is not async and handles its own loop


if __name__ == "__main__":
    # The main() function now contains app.run_polling() which is not async
    # So, we just call main() directly. asyncio.run() is typically used when
    # main() itself is an async function and needs to be awaited.
    # For python-telegram-bot v20+, app.run_polling() handles the event loop.
    main()