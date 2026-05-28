from datetime import datetime, timedelta
import logging
from aiogram import Bot
from database import get_db, get_clients_for_reminder, update_reminder_status

logger = logging.getLogger(__name__)

async def check_and_send_reminders(bot: Bot):
    logger.info("Проверка клиентов для напоминаний...")
    with next(get_db()) as db:
        clients_to_notify = get_clients_for_reminder(db)

    for client in clients_to_notify:
        try:
            # Отправляем сообщение клиенту
            await bot.send_message(
                chat_id=client.telegram_user_id,
                text="Здравствуйте, это Раиль, ваш поставщик по технике Керхер. Хотел узнать, как у вас работает наше оборудование, всё ли хорошо, нужны ли расходники или, может быть, подбор нового оборудования на перспективу. Напишите в чат — если что-то нужно.",
                reply_markup=get_main_menu_keyboard() # Отправляем главное меню как кнопки
            )
            logger.info(f"Напоминание отправлено клиенту {client.name} ({client.telegram_user_id})")

            # Обновляем статус и дату следующего напоминания
            next_date = datetime.utcnow() + timedelta(days=client.reminder_interval_days)
            update_reminder_status(db, client.id, "Ждёт", next_date)

        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания клиенту {client.telegram_user_id}: {e}")
