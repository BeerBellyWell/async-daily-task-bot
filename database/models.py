from sqlalchemy import Column, String, Integer, Boolean, ForeignKey

from database.db import Base


class User(Base):
    user_telegram_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)


class Task(Base):
    title = Column(String(128))
    close = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey(
        'user.id', name='fk_dailytask_user_id_user'
    ))
