import logging
import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import register_handlers
from config import TOKEN
# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

register_handlers(dp)

if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
