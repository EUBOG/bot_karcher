from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import config

engine = create_engine(config.config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, unique=True, index=True)
    first_entry_date = Column(DateTime, default=datetime.utcnow)
    name = Column(String, default="")
    username = Column(String, default="")
    phone_number = Column(String) # Обязательно после подтверждения
    company = Column(String, default="")
    comment = Column(String, default="")
    last_activity = Column(DateTime, default=datetime.utcnow)
    responsible_manager = Column(String, default="")

    # Поля для напоминаний
    reminder_enabled = Column(Boolean, default=True)
    next_reminder_date = Column(DateTime)
    reminder_interval_days = Column(Integer, default=30)
    reminder_text = Column(String, default="")
    last_reminder_sent = Column(DateTime)
    reminder_status = Column(String, default="Активен") # Активен, Ждёт, Ответил, Не актуально
    bot_activity_status = Column(String, default="Ничего не выбрал") # Ничего, Выбрал, Оставил заявку


class Request(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, index=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    client_id = Column(Integer, ForeignKey('clients.id'))
    type = Column(String) # Связаться, Подбор и т.д.
    subtype = Column(String, default="")
    text = Column(String, default="")
    status = Column(String, default="Новая") # Новая, В работе, Закрыта
    responsible_manager = Column(String, default="")


def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Утилиты ---
def get_or_create_client(db: Session, user_id: int, phone_number: str, name: str = "", username: str = "", company: str = ""):
    client = db.query(Client).filter(Client.telegram_user_id == user_id).first()
    if not client:
        now = datetime.utcnow()
        # Новый клиент: статус "Ничего не выбрал", мягкое напоминание через 3 дня
        client = Client(
            telegram_user_id=user_id,
            phone_number=phone_number,
            name=name,
            username=username,
            company=company,
            reminder_status="Активен",
            bot_activity_status="Ничего не выбрал",
            next_reminder_date=now + timedelta(days=3) # Упрощённый старт для мягкого напоминания
        )
        db.add(client)
        db.commit()
        db.refresh(client)
    return client

def update_client_activity(db: Session, client_id: int, status: str):
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        client.bot_activity_status = status
        client.last_activity = datetime.utcnow()
        db.commit()

def update_reminder_status(db: Session, client_id: int, status: str, next_date: datetime = None):
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        client.reminder_status = status
        if next_date:
            client.next_reminder_date = next_date
        db.commit()

def get_clients_for_reminder(db: Session):
    now = datetime.utcnow()
    # Простая логика: все клиенты с reminder_status == "Активен" и next_reminder_date <= now
    clients = db.query(Client).filter(
        Client.reminder_enabled == True,
        Client.reminder_status == "Активен",
        Client.next_reminder_date <= now
    ).all()
    return clients

def create_request(db: Session, client_id: int, req_type: str, text: str, subtype: str = ""):
    request = Request(client_id=client_id, type=req_type, subtype=subtype, text=text)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request
