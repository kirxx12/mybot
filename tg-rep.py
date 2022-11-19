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
from settings.config import TOKEN
# from settingsForUpdates import SETTING


bot = Bot(SETTING['TOKEN'])
bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
data = IntWithDb()


class GetAndCheck(StatesGroup):
    GET_TASK = State()
    CHECK_ANSWER = State()


@dp.message_handler(commands=['start'])
async def start_with_rep_bot(message: types.Message):
    data.create_db_for_user('m' + str(message.chat.id))
    await message.answer('Привет!\nЧтобы начать введи команду /get и я выдам тебе случайное задание!'
                         + '\nЕсли возникнут сложности и ты захочешь перестать решение задания, просто введи /stop, если решаешь задание')


@dp.message_handler(commands=['stop'], state=GetAndCheck.CHECK_ANSWER)
async def stop_check_answer_random_task(message: types.Message,
                                        state: FSMContext):
    await message.answer('Надеюсь, что когда эта задача попадется тебе снова, '
                         + 'ты решишь ее')
    await state.finish()


@dp.message_handler(commands=['help'])
async def help_for_rep_bot(message: types.Message):
    await bot.send_message(message.chat.id,
                           md.text('Привет, чтобы начать, выбери одну из команд:\n'
                           + md.bold('/get') + md.text(' - получение случайного задания')
                           + md.bold('/stop') + md.text(' - остановить выполнение задания')),
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['get'])
async def start_with_rep_bot(message: types.Message,
                             state: FSMContext):
    await GetAndCheck.GET_TASK.set()
    random_task = data.get_random_not_done_task('m'+ str(message.chat.id))
    if random_task[0] == '0':
        task = 'Задания кончились, можно ложиться спать!'
        await message.answer(task)
        await state.finish()
    else:
        photo = open(str(random_task[3]), 'rb')
        async with state.proxy() as dt:
            dt['id_task'] = random_task[0]
        await GetAndCheck.next()
        await bot.send_message(message.chat.id,
                               f'{random_task[1]}')
        await bot.send_photo(message.chat.id,
                             photo)


@dp.message_handler(state=GetAndCheck.CHECK_ANSWER)
async def check_answer_random_task(message: types.Message,
                                   state: FSMContext):
    async with state.proxy() as dt:
        if data.check_answer(dt['id_task'], message.text, 'm' + str(message.chat.id)):
            await message.answer('Все верно!:) Молодчинка')
            await state.finish()
        else:
            await message.answer('Неверно!\nПопробуй ещё раз')


while __name__ == '__main__':
    executor.start_polling(dp)
