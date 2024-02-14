import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup


load_dotenv()


class TaskState(StatesGroup):
    new_task = State()
    del_task = State()
    select_task_for_edit = State()
    new_title_for_edit_task = State()
    get_tasks = State()


bot = AsyncTeleBot(
    token=os.getenv('TOKEN'), state_storage=StateMemoryStorage()
)
