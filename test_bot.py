# test_bot.py (или main.py для теста)

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import os
from dotenv import load_dotenv # Если вы хотите использовать .env, хотя для теста можно и без

# load_dotenv() # Раскомментируйте, если используете .env

# Укажите ваш токен напрямую здесь или загрузите из переменной окружения
# Рекомендуется использовать переменную окружения на сервере
BOT_TOKEN = os.getenv("BOT_TOKEN") # На сервере убедитесь, что переменная окружения BOT_TOKEN установлена
# BOT_TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE" # Альтернатива (менее безопасно)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хендлер для команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Это тестовый бот. Подключение к Telegram работает!")

# Основная функция запуска
async def main():
    print("Starting test bot polling...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())