from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards.default_keyboards import get_start_keyboard, get_main_menu_keyboard, get_back_to_menu_keyboard
from database import get_db, get_or_create_client, update_client_activity
from contextlib import contextmanager

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Здравствуйте, это Раиль, ваш поставщик по технике Керхер и другому моющему оборудованию. Через этого бота вы можете быстро связаться со мной, запросить коммерческое предложение, оставить запрос на демонстрацию, подобрать оборудование и заказать расходники.")
    await message.answer("Для продолжения, пожалуйста, подтвердите ваш номер телефона кнопкой ниже.", reply_markup=get_start_keyboard())

@router.message(F.contact)
async def contact_received(message: Message):
    if message.from_user.id != message.contact.user_id:
        await message.answer("Пожалуйста, подтвердите свой номер, нажав кнопку.")
        return

    phone_number = message.contact.phone_number
    with next(get_db()) as db:
        client = get_or_create_client(
            db, message.from_user.id, phone_number,
            name=message.from_user.full_name,
            username=message.from_user.username
        )
        # Обновляем статус после получения контакта
        update_client_activity(db, client.id, "Выбрал сценарий")

    await message.answer("Спасибо. Выберите, с чем вам помочь.", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "Вернуться в главное меню")
async def back_to_menu(message: Message):
    await message.answer("Вы в главном меню.", reply_markup=get_main_menu_keyboard())
