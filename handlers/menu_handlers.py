from aiogram import Router, F
from aiogram.types import Message
from keyboards.default_keyboards import get_contact_scenario_keyboard, get_file_upload_keyboard, get_back_to_menu_keyboard, get_start_over_or_exit_keyboard, get_main_menu_keyboard
from database import get_db, update_client_activity, create_request
from contextlib import contextmanager
from database import Client

router = Router()

# --- Вспомогательная функция ---
async def handle_scenario_selection(message: Message, scenario_name: str, response_text: str, keyboard_func):
    with next(get_db()) as db:
        # Предполагаем, что у клиента есть способ получения его ID, например, через состояние или снова запрос в БД
        # Для простоты, пока просто обновим статус
        # TODO: Получить client.id из базы по message.from_user.id
        # client = db.query(Client).filter(Client.telegram_user_id == message.from_user.id).first()
        # if client:
        #     update_client_activity(db, client.id, "Выбрал сценарий")
        pass # Пока пропустим обновление, так как не получили client.id
    await message.answer(response_text)
    if keyboard_func:
        await message.answer("Выберите действие:", reply_markup=keyboard_func())

# --- Обработчики ---
@router.message(F.text == "Связаться")
async def menu_connect(message: Message):
    await handle_scenario_selection(
        message,
        "Связаться",
        "Выберите способ связи:",
        get_contact_scenario_keyboard
    )

@router.message(F.text == "Перезвоните мне")
async def connect_callback(message: Message):
    await message.answer("При желании можете кратко написать тему обращения.")
    # Переход в состояние ожидания текста (реализуется через FSM в aiogram, опционально)
    # Пока просто обновим статус и покажем финальное сообщение
    with next(get_db()) as db:
        client = db.query(Client).filter(Client.telegram_user_id == message.from_user.id).first()
        if client:
            update_client_activity(db, client.id, "Оставил заявку")
    await message.answer("Спасибо, ваш запрос отправлен. Я постараюсь оперативно ответить в этом чате.", reply_markup=get_back_to_menu_keyboard())

@router.message(F.text == "Написать менеджеру")
async def connect_write(message: Message):
    await message.answer("Напишите ваш вопрос, и я постараюсь оперативно ответить.")
    # Здесь бот ждёт следующее сообщение от пользователя
    # Пока просто обновим статус и покажем финальное сообщение
    with next(get_db()) as db:
        client = db.query(Client).filter(Client.telegram_user_id == message.from_user.id).first()
        if client:
            update_client_activity(db, client.id, "Оставил заявку")
    await message.answer("Спасибо, ваш запрос отправлен. Я постараюсь оперативно ответить в этом чате.", reply_markup=get_back_to_menu_keyboard())

@router.message(F.text == "Проработать по смете")
async def menu_procurement_estimate(message: Message):
    await handle_scenario_selection(
        message,
        "Проработать по смете",
        "Прикрепите файл сметы или ТХ для проработки.",
        get_file_upload_keyboard
    )

@router.message(F.document) # Обработчик отправки файла
async def handle_document(message: Message):
    file_info = await message.bot.get_file(message.document.file_id)
    file_path = file_info.file_path

    # Скачивание файла (опционально, можно просто сохранить file_id)
    # await message.bot.download_file(file_path, f"downloads/{message.document.file_name}")

    with next(get_db()) as db:
        client = db.query(Client).filter(Client.telegram_user_id == message.from_user.id).first()
        if client:
            # Сохраняем запрос типа "Проработать по смете" с файлом
            create_request(db, client.id, "Проработать по смете", f"Приложен файл: {message.document.file_name}", "Файл сметы/ТХ")
            update_client_activity(db, client.id, "Оставил заявку")

    await message.answer("Файл получен. Спасибо, ваш запрос отправлен. Я постараюсь оперативно ответить в этом чате.", reply_markup=get_back_to_menu_keyboard())



# --- НОВЫЙ ОБРАБОТЧИК: Начать с начала (как /start) ---
@router.message(F.text == "Начать с начала")
async def start_over(message: Message):
    """
    Повторяет логику команды /start.
    """
    # Проверяем, есть ли у пользователя подтвержденный контакт в базе
    with next(get_db()) as db:
        client = db.query(Client).filter(Client.telegram_user_id == message.from_user.id).first()

    if client and client.phone_number: # Если клиент найден и у него есть подтверждённый номер
        # Пропускаем просьбу подтвердить номер, сразу показываем главное меню
        await message.answer("Выберите, с чем вам помочь.", reply_markup=get_main_menu_keyboard())
        # Обновляем статус, если нужно (например, сбросить до "Ничего не выбрал")
        # update_client_activity(db, client.id, "Ничего не выбрал")
    else:
        # Если контакт не найден или не подтверждён, повторяем начальный сценарий
        await message.answer("Здравствуйте, это Раиль, ваш поставщик по технике Керхер и другому моющему оборудованию. Через этого бота вы можете быстро связаться со мной, запросить коммерческое предложение, оставить запрос на демонстрацию, подобрать оборудование и заказать расходники.")
        await message.answer("Для продолжения, пожалуйста, подтвердите ваш номер телефона кнопкой ниже.", reply_markup=get_start_keyboard())

# --- НОВЫЙ ОБРАБОТЧИК: Завершить работу ---
@router.message(F.text == "Завершить работу с ботом")
async def end_conversation(message: Message):
    """
    Отправляет сообщение и завершает текущую сессию (до следующего /start или сообщения).
    """
    await message.answer("Спасибо за тестирование.")

# --- Обработка неизвестных команд/кнопок ---
@router.message(F.text)
async def unknown_command_handler(message: Message):
    """
    Обработчик для любых текстовых сообщений, не подходящих под другие фильтры.
    """
    await message.answer("Алгоритм ещё дорабатывается.")
    await message.answer("Что вы хотите сделать?", reply_markup=get_start_over_or_exit_keyboard())


# Добавьте остальные обработчики меню по аналогии...
