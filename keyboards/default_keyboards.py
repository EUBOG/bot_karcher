from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

def get_start_keyboard():
    keyboard = [
        [KeyboardButton(text="Начать", request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="Связаться")],
        [KeyboardButton(text="Подбор оборудования/ оснащение объекта")],
        [KeyboardButton(text="Нужна демонстрация")],
        [KeyboardButton(text="Запрос коммерческого предложения")],
        [KeyboardButton(text="Расходники")],
        [KeyboardButton(text="Вопрос по документам")],
        [KeyboardButton(text="Сервис")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_back_to_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="Вернуться в главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_contact_scenario_keyboard():
    keyboard = [
        [KeyboardButton(text="Перезвоните мне")],
        [KeyboardButton(text="Написать менеджеру")],
        [get_back_to_menu_keyboard().keyboard[0][0]] # Кнопка "Вернуться в главное меню"
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_file_upload_keyboard():
    # Кнопка для отправки файла
    keyboard = [
        [KeyboardButton(text="Прикрепить файл сметы или ТХ")], # Пример
        [get_back_to_menu_keyboard().keyboard[0][0]]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
