from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from config import API_TOKEN
from handlers import register_handlers
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from database import setup_db  # Импортируем функцию для настройки БД
from scheduler import start_scheduler  # Импортируем планировщик
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Импортируем MemoryStorage


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()  # Создаем экземпляр MemoryStorage
dp = Dispatcher(bot, storage=storage)  # Передаем storage в Dispatcher

# Настраиваем базу данных
setup_db()  # Создаем базу данных и таблицы, если они не существуют

# Добавление логгирования
dp.middleware.setup(LoggingMiddleware())

# Регистрация команд
register_handlers(dp)

if __name__ == '__main__':
    # Запуск планировщика напоминаний
    start_scheduler(bot)
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
