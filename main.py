import asyncio

from telebot import asyncio_filters

from bot.handlers import bot_handlers  # noqa
from bot.core.config import bot


if __name__ == "__main__":
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    asyncio.run(bot.infinity_polling())
