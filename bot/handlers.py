            import json
            from telegram import Update
            from telegram.ext import ContextTypes, ConversationHandler
            from datetime import datetime

            # Import utility functions
            from utils import load_tasks, save_tasks, generate_task_id, get_current_timestamp, parse_datetime_input

            # Define states for the conversation
            TITLE, DESCRIPTION, CATEGORY, DUE_DATE, REMINDER_TIME = range(5)

            # /start
            async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Sends a welcome message and lists available commands."""
                await update.message.reply_text(
                    "سلام! 👋 من بات مدیریت تسک‌هام.\n"
                    "دستورها:\n"
                    "/add - برای اضافه کردن تسک جدید (به صورت مرحله به مرحله)\n"
                    "/list - نمایش لیست تسک‌ها\n"
                    "/delete [ID تسک] - حذف تسک با استفاده از ID آن\n"
                    "/cancel - برای لغو عملیات اضافه کردن تسک"
                )

            # --- Conversation Handler for /add command ---

            async def add_command_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Starts the conversation for adding a new task."""
                # Initialize a dictionary to store task details during the conversation
                context.user_data['current_task'] = {}
                await update.message.reply_text("عنوان تسک را وارد کنید:")
                return TITLE

            async def ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Asks for the task description after getting the title."""
                title = update.message.text
                if not title:
                    await update.message.reply_text("عنوان نمی‌تواند خالی باشد. لطفاً دوباره عنوان را وارد کنید:")
                    return TITLE # Stay in the same state if input is invalid

                context.user_data['current_task']['title'] = title
                await update.message.reply_text("توضیحات تسک را وارد کنید (اختیاری):")
                return DESCRIPTION

            async def ask_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Asks for the task category after getting the description."""
                description = update.message.text
                # Description can be empty
                context.user_data['current_task']['description'] = description if description else ""
                await update.message.reply_text("دسته‌بندی تسک را وارد کنید (مثال: hw, work, personal):")
                return CATEGORY

            async def ask_due_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Asks for the due date after getting the category."""
                category = update.message.text
                if not category:
                    await update.message.reply_text("دسته‌بندی نمی‌تواند خالی باشد. لطفاً دوباره دسته‌بندی را وارد کنید:")
                    return CATEGORY # Stay in the same state if input is invalid

                context.user_data['current_task']['category'] = category
                await update.message.reply_text("تاریخ و زمان سررسید را وارد کنید (مثال: 2025-06-01 20:00 یا 2025-06-01):")
                return DUE_DATE

            async def ask_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Asks for the reminder time after getting the due date."""
                due_date_str = update.message.text
                parsed_due_date = parse_datetime_input(due_date_str)

                if not parsed_due_date:
                    await update.message.reply_text(
                        "فرمت تاریخ و زمان سررسید نامعتبر است. لطفاً از فرمت 'YYYY-MM-DD HH:MM' یا 'YYYY-MM-DD' استفاده کنید:"
                    )
                    return DUE_DATE # Stay in the same state if input is invalid

                context.user_data['current_task']['due_date'] = parsed_due_date.isoformat(timespec='seconds')
                await update.message.reply_text("تاریخ و زمان یادآوری را وارد کنید (اختیاری، مثال: 2025-05-31 20:00):")
                return REMINDER_TIME

            async def save_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Finalizes and saves the new task."""
                reminder_time_str = update.message.text
                parsed_reminder_time = parse_datetime_input(reminder_time_str)

                if reminder_time_str and not parsed_reminder_time: # If user provided input but it's invalid
                    await update.message.reply_text(
                        "فرمت تاریخ و زمان یادآوری نامعتبر است. لطفاً از فرمت 'YYYY-MM-DD HH:MM' یا 'YYYY-MM-DD' استفاده کنید یا خالی بگذارید:"
                    )
                    return REMINDER_TIME # Stay in the same state if input is invalid

                context.user_data['current_task']['reminder_time'] = parsed_reminder_time.isoformat(timespec='seconds') if parsed_reminder_time else ""

                # Add auto-generated fields
                context.user_data['current_task']['id'] = generate_task_id()
                context.user_data['current_task']['created_at'] = get_current_timestamp()

                # Load existing tasks, add the new one, and save
                tasks = load_tasks()
                tasks.append(context.user_data['current_task'])
                save_tasks(tasks)

                await update.message.reply_text(f"✅ تسک '{context.user_data['current_task']['title']}' اضافه شد!")

                # Clear user data for the current task
                del context.user_data['current_task']
                return ConversationHandler.END # End the conversation

            async def cancel_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Cancels the task addition process."""
                if 'current_task' in context.user_data:
                    del context.user_data['current_task']
                await update.message.reply_text("عملیات اضافه کردن تسک لغو شد.")
                return ConversationHandler.END

            # --- End of Conversation Handler ---

            # /list
            async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Lists all current tasks."""
                tasks = load_tasks()

                if not tasks:
                    await update.message.reply_text("📭 لیست تسک‌ها خالیه.")
                    return

                message_parts = ["📝 لیست تسک‌ها:"]
                for i, t in enumerate(tasks):
                    title = t.get('title', 'بدون عنوان')
                    task_id = t.get('id', 'N/A')
                    category = t.get('category', 'بدون دسته‌بندی')
                    due_date = t.get('due_date', 'نامشخص')

                    # Format due date for display if it exists
                    if due_date and due_date != 'نامشخص':
                        try:
                            dt_obj = datetime.fromisoformat(due_date)
                            due_date_formatted = dt_obj.strftime('%Y-%m-%d %H:%M')
                        except ValueError:
                            due_date_formatted = due_date # Keep as is if parsing fails
                    else:
                        due_date_formatted = 'نامشخص'

                    message_parts.append(
                        f"**{i+1}. {title}** (ID: `{task_id}`)\n"
                        f"   دسته‌بندی: {category}\n"
                        f"   سررسید: {due_date_formatted}"
                    )

                await update.message.reply_markdown_v2("\n".join(message_parts))


            # /delete
            async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Deletes a task by its ID."""
                if not context.args:
                    await update.message.reply_text("❗️ لطفاً ID تسک رو وارد کن. مثال: /delete <ID تسک>")
                    return

                task_id_to_delete = context.args[0]
                tasks = load_tasks()

                initial_task_count = len(tasks)
                # Filter out the task with the given ID
                updated_tasks = [t for t in tasks if t.get('id') != task_id_to_delete]

                if len(updated_tasks) < initial_task_count:
                    save_tasks(updated_tasks)
                    await update.message.reply_text(f"🗑 تسک با ID `{task_id_to_delete}` حذف شد.")
                else:
                    await update.message.reply_text(f"❗️ تسکی با ID `{task_id_to_delete}` پیدا نشد.")