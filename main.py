import asyncio
import pytz
WIB = pytz.timezone("Asia/Jakarta")
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
import database
from handlers import (
    start_command,
    help_command,
    list_command,
    hapus_command,
    get_conversation_handler,
    error_handler,
)
from scheduler import reminder_job

async def post_init(application: Application):
    """Run after bot initialization."""
    application.job_queue.run_repeating(reminder_job, interval=30, first=10)
    print("✅ Scheduler started - reminder will check every minute")

def main():
    """Main function to run the bot."""
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN tidak ditemukan!")
        print("Silakan buat file .env dengan BOT_TOKEN=your_token")
        return
    
    database.init_db()
    print("✅ Database initialized")
    
    application = (
    Application.builder()
    .token(BOT_TOKEN)
    .post_init(post_init)
    .build()
)
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("hapus", hapus_command))
    application.add_handler(get_conversation_handler())
    application.add_error_handler(error_handler)
    
    print("🤖 Bot started...")
    print("Commands: /start, /tambah, /list, /hapus")
    
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
