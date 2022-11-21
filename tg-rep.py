import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram import executor
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.utils.exceptions import BadRequest
from create_db_for_rep import IntWithDb
from settings.config import TOKEN
from sqlite3 import OperationalError
# from settingsForUpdates import SETTING



# bot = Bot(SETTING['TOKEN'])
bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
data = IntWithDb()


class GetAndCheckMATH(StatesGroup):
    GET_TASK = State()
    CHECK_ANSWER_MATH = State()


class GetAndCheckINFO(StatesGroup):
    GET_TASK = State()
    CHECK_ANSWER_INFO = State()


@dp.message_handler(commands=['start'])
async def start_with_rep_bot(message: types.Message):
    btn1 = KeyboardButton('/create_math_base')
    btn2 = KeyboardButton('/create_info_base')
    start_btns = ReplyKeyboardMarkup(resize_keyboard=True)
    start_btns.add(btn1, btn2)
    await message.answer('Привет!\nЧтобы начать выбери одну из команд и я расскажу, '
                         + '\nчто ты можешь тут делать:)'
                         + '\n/create_math_base - начать подготовку к математике'
                         + '\n/create_info_base - начать подготовку к информатике',
                         reply_markup=start_btns)


@dp.message_handler(commands=['stop'], state=GetAndCheckMATH.CHECK_ANSWER_MATH)
async def stop_check_answer_random_task(message: types.Message,
                                        state: FSMContext):
    await message.answer('Надеюсь, что когда эта задача попадется тебе снова, '
                         + 'ты решишь ее',
                         reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=['stop'], state=GetAndCheckINFO.CHECK_ANSWER_INFO)
async def stop_check_answer_random_task(message: types.Message,
                                        state: FSMContext):
    await message.answer('Надеюсь, что когда эта задача попадется тебе снова, '
                         + 'ты решишь ее',
                         reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=['delete'])
async def delete_table_for_user(message: types.Message):
    data.delete_db('i' + str(message.chat.id))
    data.delete_db('m' + str(message.chat.id))
    await message.answer('Готово!')


@dp.message_handler(commands=['help'])
async def help_for_rep_bot(message: types.Message):
    await bot.send_message(message.chat.id,
                           md.text('Привет, чтобы начать, выбери одну из команд:\n'
                           + md.bold('/get') + md.text(' - получение случайного задания')
                           + md.bold('/stop') + md.text(' - остановить выполнение задания')),
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['create_math_base'])
async def start_with_math(message: types.Message):
    data.create_db_for_user('m' + str(message.chat.id), 'm_tasks')
    btn = KeyboardButton('/getm')
    mathstart_btns = ReplyKeyboardMarkup(resize_keyboard=True).add(btn)
    await message.answer('Отлично, я создал для тебя базу и заполнил заданиями'
                         + '\nТеперь давай попробуем что-нибудь решить!'
                         + '\nВведи /getm, чтобы получить случайный номер по мат-ке',
                         reply_markup=mathstart_btns)


@dp.message_handler(commands=['create_info_base'])
async def start_with_info(message: types.Message):
    data.create_db_for_user('i' + str(message.chat.id), 'i_tasks')
    btn = KeyboardButton('/geti')
    infostart_btns = ReplyKeyboardMarkup(resize_keyboard=True).add(btn)
    await message.answer('Отлично, я создал для тебя базу и заполнил заданиями'
                         + '\nТеперь давай попробуем что-нибудь решить!'
                         + '\nВведи /geti, чтобы получить случайный номер по инфе',
                         reply_markup=infostart_btns)


@dp.message_handler(commands=['geti'])
async def get_task_info(message: types.Message,
                        state: FSMContext):
    await GetAndCheckINFO.GET_TASK.set()
    
    try:
        random_task = data.get_random_not_done_task('i' + str(message.chat.id),
                                                    'i_tasks')
    except OperationalError:
        btn = KeyboardButton('/create_info_base')
        kb = ReplyKeyboardMarkup(resize_keyboard=True).add(btn)
        await state.finish()
        await message.answer('Таблица не создана'
                             + '\nСоздай базу',
                             reply_markup=kb)
    except:
        await state.finish()
        await message.answer('Что-то пошло не так:(')
    else:
        if random_task[0] == '0':
            task = 'Задания кончились, можно ложиться спать!'
            await message.answer(task, reply_markup=ReplyKeyboardRemove())
            await state.finish()
        else:
            photo = open(str(random_task[3]), 'rb')
            async with state.proxy() as dt:
                dt['id_task'] = random_task[0]
            await GetAndCheckINFO.next()
            btn = KeyboardButton('/stop')
            geti_btns = ReplyKeyboardMarkup(resize_keyboard=True).add(btn)
            await bot.send_message(message.chat.id,
                                   f'{random_task[1]}'
                                   + '\nЧтобы прекратить выполнение, напиши /stop',
                                   reply_markup=geti_btns)
            await bot.send_photo(message.chat.id, photo=photo)


@dp.message_handler(state=GetAndCheckINFO.CHECK_ANSWER_INFO)
async def check_answer_info_random_task(message: types.Message,
                                        state: FSMContext):
    async with state.proxy() as dt:
        if data.check_answer(dt['id_task'], message.text, 'i' + str(message.chat.id), 'i_tasks'):
            await message.answer('Все верно! Молодчинка:)', reply_markup=ReplyKeyboardRemove())
            await state.finish()
        else:
            await message.answer('Пока неверно, попробуй еще разок')


@dp.message_handler(commands=['getm'])
async def get_task_math(message: types.Message,
                             state: FSMContext):
    await GetAndCheckMATH.GET_TASK.set()
    try:
        random_task = data.get_random_not_done_task('m'+ str(message.chat.id),
                                                    'm_tasks')
    except OperationalError:
        btn = KeyboardButton('/create_math_base')
        kb = ReplyKeyboardMarkup(resize_keyboard=True).add(btn)
        await state.finish()
        await message.answer('Таблица не создана'
                             + '\nСоздай базу',
                             reply_markup=kb)
    except:
        await state.finish()
        await message.answer('Что-то пошло не так:(')
    else:    
        if random_task[0] == '0':
            task = 'Задания кончились, можно ложиться спать!'
            await message.answer(task, reply_markup=ReplyKeyboardRemove())
            await state.finish()
        else:
            photo = open(str(random_task[3]), 'rb')
            async with state.proxy() as dt:
                dt['id_task'] = random_task[0]
            await GetAndCheckMATH.next()
            btn = KeyboardButton('/stop')
            getm_btns = ReplyKeyboardMarkup(resize_keyboard=True).add(btn)
            await bot.send_message(message.chat.id,
                                   f'{random_task[1]}'
                                   + '\nЧтобы прекратить выполнение, напиши /stop',
                                   reply_markup=getm_btns)
            await bot.send_photo(message.chat.id,
                             photo)


@dp.message_handler(state=GetAndCheckMATH.CHECK_ANSWER_MATH)
async def check_answer_math_random_task(message: types.Message,
                                   state: FSMContext):
    async with state.proxy() as dt:
        if data.check_answer(dt['id_task'], message.text, 'm' + str(message.chat.id), 'm_tasks'):
            await message.answer('Все верно!:) Молодчинка', reply_markup=ReplyKeyboardRemove())
            await state.finish()
        else:
            await message.answer('Неверно!\nПопробуй ещё раз')


while __name__ == '__main__':
    executor.start_polling(dp)
