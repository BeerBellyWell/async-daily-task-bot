from telebot import types

from bot.core.config import TaskState
from bot.core.config import bot
from bot.constants.constants import (
    HELP_TEXT,
)
from bot.validators.validators import list_tasks_in_str
from bot.crud.crud import (
    get_user_id, create_user,
    get_open_tasks,
)


@bot.message_handler(commands=['start'])
async def start(message):
    """Запустить бота."""
    user_id = await get_user_id(message)

    if user_id is None:
        await create_user(message)

    await bot.send_message(
        message.chat.id,
        f'Привет, {message.from_user.first_name}!',
    )


@bot.message_handler(commands=['help'])
async def help(message):
    """Получить помощь."""
    await bot.send_message(
        message.chat.id,
        HELP_TEXT
    )


@bot.message_handler(commands=['create_task'])
async def create_task(message):
    """Создать таску"""
    await bot.set_state(
        message.from_user.id,
        TaskState.new_task, message.chat.id
    )
    await bot.send_message(
        message.chat.id,
        'Напиши таску',
    )


@bot.message_handler(commands=['get_tasks'])
async def get_tasks(message):
    """Получить список тасок"""
    tasks_title = await get_open_tasks(message)

    tasks_string = list_tasks_in_str(tasks_title)

    if not tasks_string:
        await bot.send_message(message.chat.id, 'В списке тасков ничего нет.')
    else:
        await bot.send_message(
            message.chat.id,
            'Вот список тасков, которые нужно сделать 👇'
        )
        await bot.send_message(message.chat.id, f'{tasks_string}')


@bot.message_handler(commands=['delete_task'])
async def delete_task(message):
    """Удалить таску"""

    tasks_title = await get_open_tasks(message)

    if tasks_title == []:
        await bot.send_message(
            message.chat.id,
            'Все таски завершены!'
        )
        await bot.delete_state(message.from_user.id, message.chat.id)

    else:
        await bot.set_state(
            message.from_user.id,
            TaskState.del_task, message.chat.id
        )

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True
        )

        for btn in tasks_title:
            markup.add(types.KeyboardButton(btn))

        await bot.send_message(
            message.chat.id,
            'Выбери таску, которую нужно удалить.',
            reply_markup=markup)


@bot.message_handler(commands=['edit_task'])
async def edit_task(message):
    """Отредактировать таску"""
    tasks_title = await get_open_tasks(message)

    if tasks_title == []:
        await bot.send_message(
            message.chat.id,
            'Нет тасок для редактирования!'
        )

    else:
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True
        )

        for btn in tasks_title:
            markup.add(types.KeyboardButton(btn))

        await bot.set_state(
            message.from_user.id,
            TaskState.select_task_for_edit,
            message.chat.id
        )

        await bot.send_message(
            message.chat.id,
            'Выбери таску, которую нужно отредактировать.',
            reply_markup=markup
        )


@bot.message_handler()
async def random_text_from_user(message):
    """Ответить на непредусмотренную команду."""
    await bot.send_message(
        message.chat.id,
        f'{message.from_user.first_name}, я не понимаю, воспользуйся /help '
        f'чтобы узнать, что я могу делать.'
    )
