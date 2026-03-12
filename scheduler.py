from datetime import datetime, timedelta
import pytz
import database

WIB = pytz.timezone("Asia/Jakarta")

REMINDER_TIMES = {
    "3_hari": timedelta(days=3),
    "1_hari": timedelta(days=1),
    "6_jam": timedelta(hours=6),
    "3_jam": timedelta(hours=3),
    "1_jam": timedelta(hours=1),
    "30_menit": timedelta(minutes=30),
}

REMINDER_TEXT = {
    "3_hari": "3 HARI LAGI",
    "1_hari": "1 HARI LAGI",
    "6_jam": "6 JAM LAGI",
    "3_jam": "3 JAM LAGI",
    "1_jam": "1 JAM LAGI",
    "30_menit": "30 MENIT LAGI",
}

sent_reminders = set()


async def check_and_send_reminders(application):
    tasks = database.get_all_tasks()

    now = datetime.now(WIB)
    bot = application.bot

    for task in tasks:
        task_id, user_id, mata_kuliah, nama_tugas, deadline_str = task

        try:
            deadline = WIB.localize(datetime.strptime(deadline_str, "%Y-%m-%d %H:%M"))
        except:
            continue

        if deadline < now:
            continue

        for reminder_name, delta in REMINDER_TIMES.items():

            reminder_time = deadline - delta
            reminder_key = f"{task_id}_{reminder_name}"

            if now >= reminder_time and reminder_key not in sent_reminders:

                reminder_text = REMINDER_TEXT.get(reminder_name, "")

                message = (
                    f"⏰ PENGINGAT {reminder_text}!\n\n"
                    f"📚 {mata_kuliah}\n"
                    f"📝 {nama_tugas}\n"
                    f"📅 Deadline: {deadline.strftime('%d/%m/%Y %H:%M')}\n\n"
                    f"Segera kerjakan sebelum terlambat!"
                )

                try:
                    await bot.send_message(chat_id=user_id, text=message)
                    sent_reminders.add(reminder_key)

                    print(f"Reminder sent -> {task_id} {reminder_name}")

                except Exception as e:
                    print(e)


async def reminder_job(application):
    await check_and_send_reminders(application)