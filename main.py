import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from database import init_db
import handlers.start_handler
import handlers.menu_handlers
import handlers.file_handlers
from services.reminder_scheduler import check_and_send_reminders

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Инициализация базы данных
    init_db()

    # Создание бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация маршрутов
    dp.include_router(handlers.start_handler.router)
    dp.include_router(handlers.menu_handlers.router)
    dp.include_router(handlers.file_handlers.router)

    # Инициализация планировщика
    scheduler = AsyncIOScheduler(timezone='UTC') # Можно выбрать часовой пояс
    # Проверяем каждые 10 минут (можно увеличить интервал в проде)
    scheduler.add_job(check_and_send_reminders, trigger='interval', minutes=10, args=[bot])

    # Запуск планировщика
    scheduler.start()
    logger.info("Scheduler started.")

    try:
        # Запуск поллинга
        await dp.start_polling(bot)
    finally:
        # Остановка планировщика при завершении
        scheduler.shutdown()
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())