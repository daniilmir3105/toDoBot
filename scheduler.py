from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from database import get_upcoming_tasks  # Импортируйте вашу функцию для получения задач

async def send_reminders(bot):
    tasks = get_upcoming_tasks()  # Получаем предстоящие задачи
    for task in tasks:
        user_id = task[1]  # Предполагаем, что user_id хранится в базе данных
        task_description = task[2]
        await bot.send_message(user_id, f"Напоминание: задача '{task_description}' скоро должна быть выполнена!")

def start_scheduler(bot):
    scheduler = AsyncIOScheduler()
    # Запускаем функцию send_reminders каждую минуту
    scheduler.add_job(send_reminders, 'cron', minute='*', args=[bot])
    scheduler.start()
