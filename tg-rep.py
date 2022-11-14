import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram import executor
from random import randint
from create_db_for_rep import IntWithDb
from config import TOKEN
# from settingsForUpdates import SETTING



bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
data = IntWithDb()


class DoneTask(StatesGroup):
    GET_TASK = State()
    CHECK_ANSWER = State()


@dp.message_handler(commands=['start'])
async def start_with_rep_bot(message: types.Message):
    await message.answer('Привет! Чтобы начать введи команду /get и я выдам тебе случайное задание!')


@dp.message_handler(commands=['help'])
async def help_for_rep_bot(message: types.Message):
    await bot.send_message(message.chat.id,
                           md.text('Привет, чтобы начать, выбери одну из команд:\n'
                           + md.bold('/get') + md.text(' - получение случайного задания')),
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['get'])
async def start_with_rep_bot(message: types.Message,
                             state: FSMContext):
    await DoneTask.GET_TASK.set()
    random_task = data.get_random_not_done_task()
    task = f'Номер задания: {random_task[0]}\nУсловие:\n{random_task[1]}'
    async with state.proxy() as dt:
        dt['id_task'] = random_task[0]
    await message.answer(task)
    await DoneTask.next()


@dp.message_handler(state=DoneTask.CHECK_ANSWER)
async def check_answer_random_task(message: types.Message,
                                   state: FSMContext):
    async with state.proxy() as dt:
        if data.check_answer(dt['id_task'], message.text):
            await message.answer('Все верно!:) Молодчинка')
            await state.finish()
        else:
            await message.answer('Неверно:(\n')


while __name__ == '__main__':
    executor.start_polling(dp)