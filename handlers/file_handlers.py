# Уже частично реализовано в menu_handlers.py для документа
# Можно вынести общую логику сюда, если она усложнится
from aiogram import Router, F
from aiogram.types import Message
from database import get_db, update_client_activity, create_request
from contextlib import contextmanager

router = Router()

# Уже есть обработчик F.document в menu_handlers.py
# Если нужна универсальная обработка файлов вне сценариев:
@router.message(F.photo | F.video | F.audio)
async def handle_media_file(message: Message):
    await message.answer("Я получил медиафайл, но для обработки запроса, пожалуйста, используйте соответствующие кнопки в меню.")
