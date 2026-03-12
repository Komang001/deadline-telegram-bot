from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import database
from datetime import datetime
import pytz
WIB = pytz.timezone("Asia/Jakarta")

(MATA_KULIAH, NAMA_TUGAS, DEADLINE) = range(3)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 Hai! Saya bot pengingat deadline tugas kuliah.\n\n"
        "Fitur yang tersedia:\n"
        "/tambah - Tambah tugas baru\n"
        "/list - Lihat semua tugas\n"
        "/hapus - Hapus tugas\n"
        "/batal - Batalkan operasi"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await start_command(update, context)

async def tambah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation to add new task."""
    await update.message.reply_text(
        "📝 Tambah Tugas Baru\n\n"
        "Masukkan nama MATA KULIAH:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/batal")]], resize_keyboard=True)
    )
    return MATA_KULIAH

async def mata_kuliah_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mata kuliah input."""
    text = update.message.text.strip()
    if text == "/batal":
        await update.message.reply_text("❌ Operasi dibatalkan.", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]]))
        return ConversationHandler.END
    
    context.user_data["mata_kuliah"] = text
    await update.message.reply_text("Masukkan NAMA TUGAS:")
    return NAMA_TUGAS

async def nama_tugas_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle nama tugas input."""
    text = update.message.text.strip()
    if text == "/batal":
        await update.message.reply_text("❌ Operasi dibatalkan.", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]]))
        return ConversationHandler.END
    
    context.user_data["nama_tugas"] = text
    await update.message.reply_text(
        "Masukkan DEADLINE (format: YYYY-MM-DD HH:MM)\n"
        "Contoh: 2025-03-15 23:59"
    )
    return DEADLINE

async def deadline_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deadline input and save task."""
    text = update.message.text.strip()

    if text == "/batal":
        await update.message.reply_text(
            "❌ Operasi dibatalkan.",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True),
        )
        return ConversationHandler.END

    try:
        deadline = WIB.localize(datetime.strptime(text, "%Y-%m-%d %H:%M"))

        if deadline < datetime.now(WIB):
            await update.message.reply_text(
                "❌ Deadline tidak boleh di masa lalu.\nMasukkan lagi:"
            )
            return DEADLINE

    except ValueError:
        await update.message.reply_text(
            "❌ Format salah!\nGunakan: YYYY-MM-DD HH:MM\n"
            "Contoh: 2026-03-15 23:59"
        )
        return DEADLINE

    user_id = update.effective_user.id
    mata_kuliah = context.user_data["mata_kuliah"]
    nama_tugas = context.user_data["nama_tugas"]

    database.add_task(user_id, mata_kuliah, nama_tugas, text)

    await update.message.reply_text(
        f"✅ Tugas berhasil ditambahkan!\n\n"
        f"📚 {mata_kuliah}\n"
        f"📝 {nama_tugas}\n"
        f"📅 Deadline: {text}\n\n"
        f"🔔 Kamu akan mendapat pengingat 3 hari, 1 hari, dan 6 jam sebelum deadline.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True),
    )

    context.user_data.clear()
    return ConversationHandler.END

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command."""
    user_id = update.effective_user.id
    tasks = database.get_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text("📋 Kamu belum punya tugas. Gunakan /tambah untuk menambah tugas.")
        return
    
    message = "📋 DAFTAR TUGAS\n\n"
    now = datetime.now(WIB)
    
    for i, task in enumerate(tasks, 1):
        task_id, mata_kuliah, nama_tugas, deadline_str = task
    
        try:
            deadline = WIB.localize(datetime.strptime(deadline_str, "%Y-%m-%d %H:%M"))

            if deadline < now:
                status = "⏰ TERLAMBAT"
            else:
                remaining = deadline - now

                days = remaining.days
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60

                if days > 0:
                    status = f"📅 {days} hari lagi"
                elif hours > 0:
                    status = f"⏳ {hours} jam {minutes} menit lagi"
                else:
                    status = f"⚠️ {minutes} menit lagi"

        except:
            status = ""
        
        message += f"{i}. {mata_kuliah}\n"
        message += f"   {nama_tugas}\n"
        message += f"   Deadline: {deadline_str} {status}\n"
        message += f"   ID: {task_id}\n\n"
    
    await update.message.reply_text(message)

async def hapus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hapus command."""
    user_id = update.effective_user.id
    tasks = database.get_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text("📋 Kamu belum punya tugas.")
        return
    
    message = "🗑️ HAPUS TUGAS\n\nGunakan perintah:\n/hapus <id>\nContoh: /hapus 3\n\n"
    for task in tasks:
        task_id, mata_kuliah, nama_tugas, deadline_str = task
        message += f"ID {task_id}: {mata_kuliah} - {nama_tugas} ({deadline_str})\n"
    
    await update.message.reply_text(message)
    
    try:
        task_id = int(context.args[0]) if context.args else None
        if task_id:
            task = database.get_task_by_id(task_id)
            if task and task[1] == user_id:
                database.delete_task(task_id)
                await update.message.reply_text(f"✅ Tugas ID {task_id} berhasil dihapus!")
            else:
                await update.message.reply_text("❌ Tugas tidak ditemukan atau bukan milikmu.")
        else:
            await update.message.reply_text("❌ Gunakan /hapus <id>\nContoh: /hapus 1")
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Gunakan /hapus <id>\nContoh: /hapus 1")

async def batal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /batal command."""
    await update.message.reply_text("❌ Operasi dibatalkan.", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True))
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    print(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

def get_conversation_handler():
    """Get conversation handler for adding tasks."""
    return ConversationHandler(
        entry_points=[CommandHandler("tambah", tambah_command)],
        states={
            MATA_KULIAH: [MessageHandler(filters.TEXT & ~filters.COMMAND, mata_kuliah_input)],
            NAMA_TUGAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, nama_tugas_input)],
            DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, deadline_input)],
        },
        fallbacks=[CommandHandler("batal", batal_command)],
    )
