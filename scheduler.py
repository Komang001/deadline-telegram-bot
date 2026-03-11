from datetime import datetime, timedelta
import database

REMINDER_TIMES = {
    "3_hari": timedelta(days=3),
    "1_hari": timedelta(days=1),
    "6_jam": timedelta(hours=6),
}

sent_reminders = set()

async def check_and_send_reminders(application):
    """Check all tasks and send reminders if needed."""
    tasks = database.get_all_tasks()
    now = datetime.now()
    bot = application.bot
    
    for task in tasks:
        task_id, user_id, mata_kuliah, nama_tugas, deadline_str = task
        
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        
        if deadline < now:
            continue
        
        for reminder_name, reminder_delta in REMINDER_TIMES.items():
            reminder_time = deadline - reminder_delta
            reminder_key = f"{task_id}_{reminder_name}"
            
            if reminder_time <= now < reminder_time + timedelta(minutes=1):
                if reminder_key not in sent_reminders:
                    message = format_reminder_message(mata_kuliah, nama_tugas, deadline, reminder_name)
                    try:
                        await bot.send_message(chat_id=user_id, text=message)
                        sent_reminders.add(reminder_key)
                        print(f"✅ Reminder sent to {user_id}: {reminder_name}")
                    except Exception as e:
                        print(f"Error sending reminder: {e}")

def format_reminder_message(mata_kuliah: str, nama_tugas: str, deadline: datetime, reminder_type: str) -> str:
    """Format reminder message based on type."""
    deadline_formatted = deadline.strftime("%d/%m/%Y jam %H:%M")
    
    if reminder_type == "3_hari":
        reminder_text = "3 HARI LAGI"
    elif reminder_type == "1_hari":
        reminder_text = "1 HARI LAGI"
    else:
        reminder_text = "6 JAM LAGI"
    
    return f"⏰ PENGINGAT {reminder_text}!\n\n📚 {mata_kuliah}\n📝 {nama_tugas}\n📅 Deadline: {deadline_formatted}\n\nJangan lupa kerjakan!"

async def reminder_job(application):
    """Job to check and send reminders periodically."""
    await check_and_send_reminders(application)
