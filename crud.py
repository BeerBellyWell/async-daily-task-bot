from sqlalchemy import select, and_
from telebot import types

from database.models import User, Task
from core.config import bot
from validators import task_title_length_validator
from database.db import session
from core.config import TaskState


async def get_user_id(message) -> int:
    """Возвращает id пользователя."""
    user_id = await session.execute(select(User.id).where(
        User.user_telegram_id == message.from_user.id
    ))
    user_id = user_id.scalars().first()
    return user_id


async def get_open_tasks(message) -> list:
    """
    Возвращает список открытых тасков
    конкретного пользователя.
    """
    user_id = await get_user_id(message)

    tasks_title = await session.execute(select(Task.title).where(
        Task.user_id == user_id, and_(Task.close == False))
    )
    tasks_title = tasks_title.scalars().all()
    return tasks_title


async def get_task_by_title(message) -> Task:
    """
    Получить таску по title.
    """
    user_id = await get_user_id(message)

    task = await session.execute(select(Task).where(
        Task.title == message.text, and_(
            Task.close == False), and_(Task.user_id == user_id)
    ))
    task = task.scalars().first()
    return task


async def task_title_check_duplicate(message, new_task_title: str) -> int:
    """Проверка таски на уникальность."""
    user_id = await get_user_id(message)

    task = await session.execute(select(Task.id).where(
        Task.title == new_task_title, and_(
            Task.close == False), and_(Task.user_id == user_id)
    ))
    task = task.scalars().first()
    return task


async def create_user(message):
    """Создать пользователя."""
    user = User(user_telegram_id=message.from_user.id,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
                )
    session.add(user)
    await session.commit()
    await session.refresh(user)


@bot.message_handler(state=TaskState.new_task)
async def create_new_task(message):
    """Создать таску"""
    new_task_title = message.text

    if await task_title_check_duplicate(message, new_task_title) != None:
        await bot.send_message(
            message.chat.id,
            'Такая таска уже есть.'
        )
    
    elif not task_title_length_validator(new_task_title):
        await bot.send_message(
            message.chat.id,
            'Название таски не должно превышать 128 символов.'
        )
    
    else:
        user_id = await get_user_id(message)

        task = Task(title=message.text, user_id=user_id)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        await bot.send_message(
            message.chat.id,
            f'Таска "<i>{task.title}</i>" создана!',
            parse_mode='html'
        )
    
    await bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=TaskState.del_task)
async def close_selected_task(message):
    """Закрыть таску"""
    await bot.delete_state(message.from_user.id, message.chat.id)

    task = await get_task_by_title(message)
    if task == None:
        await bot.send_message(
            message.chat.id,
            f'Таски "<i>{message.text}</i>" не существует!',
            parse_mode='html',
        )
    else:
        task.close = True
        await session.commit()
        await session.refresh(task)
        await bot.send_message(
            message.chat.id,
            f'Таска "<i>{task.title}</i>" закрыта',
            parse_mode='html',
            reply_markup=types.ReplyKeyboardRemove()
        )


TASK_FOR_EDIT = None


@bot.message_handler(state=TaskState.select_task_for_edit)
async def select_task_for_edit(message):
    """
    Выбрать таску для редактирования.
    """
    global TASK_FOR_EDIT

    await bot.delete_state(message.from_user.id, message.chat.id)
    
    TASK_FOR_EDIT = await get_task_by_title(message)
    if TASK_FOR_EDIT == None:
        await bot.send_message(
            message.chat.id,
            f'Таски "<i>{message.text}</i>" не существует!',
            parse_mode='html',
        )
    
    else:
        await bot.set_state(
            message.from_user.id,
            TaskState.new_title_for_edit_task,
            message.chat.id
            )
        
        await bot.send_message(
            message.chat.id,
            'Напиши новое название таски.',
            reply_markup=types.ReplyKeyboardRemove()
            )
    

@bot.message_handler(state=TaskState.new_title_for_edit_task)
async def update_task_title(message):
    """
    Записать отредактированную таску в БД.
    """
    new_task_title = message.text

    if await task_title_check_duplicate(message, new_task_title) != None:
        await bot.send_message(
            message.chat.id,
            'Такая таска уже есть.'
        )
    
    elif not task_title_length_validator(new_task_title):
        await bot.send_message(
            message.chat.id,
            'Название таски не должно превышать 128 символов.'
        )
    
    else:
        TASK_FOR_EDIT.title = new_task_title
        await session.commit()
        await session.refresh(TASK_FOR_EDIT)
        await bot.send_message(
            message.chat.id,
            f'Таска отредактирована: "<i>{TASK_FOR_EDIT.title}</i>" ',
            parse_mode='html'
        )
    
    await bot.delete_state(message.from_user.id, message.chat.id)
