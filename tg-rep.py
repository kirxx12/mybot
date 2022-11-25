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
# from settings.settingsForUpdates import SETTING



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
    btns = [
        InlineKeyboardButton(text='Математика', callback_data='create_math_base'), 
        InlineKeyboardButton(text='Информатика', callback_data='create_info_base')
    ]
    start_btns = InlineKeyboardMarkup(row_width=1)
    start_btns.add(*btns)
    await message.answer('Привет!\nЧтобы начать выбери одну из команд и я расскажу, '
                         + '\nчто ты можешь тут делать:)',
                         reply_markup=start_btns)


@dp.callback_query_handler(text='stop',
                           state=[
                                GetAndCheckINFO.CHECK_ANSWER_INFO,
                                GetAndCheckMATH.CHECK_ANSWER_MATH
                        ])
async def stop_all_process(call: types.CallbackQuery,
                           state: FSMContext):
    btns = [
        InlineKeyboardButton(text='Вернуться', callback_data='menu')
    ]
    kb = InlineKeyboardMarkup(row_width=1).add(*btns)
    await call.message.answer(text='Надеюсь, что вскоре ты решишь эту задачу',
                              reply_markup=kb)
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


@dp.callback_query_handler(text='create_math_base')
async def start_with_math(call: types.CallbackQuery):
    data.create_db_for_user('m' + str(call.message.chat.id), 'm_tasks')
    btns = [
        InlineKeyboardButton(text='Случайноe задание', callback_data='getm'),
    ]
    kb = InlineKeyboardMarkup(row_width=1).add(*btns)
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Отлично, я создал для тебя базу и заполнил заданиями'
                           + '\nТеперь давай попробуем что-нибудь решить!',
                           reply_markup=kb)
    await call.message.delete()


@dp.callback_query_handler(text='create_info_base')
async def start_with_info(call: types.CallbackQuery):
    data.create_db_for_user('i' + str(call.message.chat.id), 'i_tasks')
    btns = [
        InlineKeyboardButton(text='Случайноe задание', callback_data='geti'),
    ]
    kb = InlineKeyboardMarkup(row_width=1).add(*btns)
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Отлично, я создал для тебя базу и заполнил заданиями'
                           + '\nТеперь давай попробуем что-нибудь решить!',
                           reply_markup=kb)
    await call.message.delete()


@dp.callback_query_handler(text='geti')
async def get_task_info(call: types.CallbackQuery,
                        state: FSMContext):
    await GetAndCheckINFO.GET_TASK.set()
    
    try:
        random_task = data.get_random_not_done_task('i'
                                                    + str(call.message.chat.id),
                                                    'i_tasks')
    except OperationalError:
        btn = InlineKeyboardButton(text='Создать базу для информатики',
                                   callback_data='create_info_base')
        kb = InlineKeyboardMarkup(row_width=1).add(btn)
        await state.finish()
        await call.message.answer('Таблица не создана'
                                  + '\nСоздай базу',
                                  reply_markup=kb)
        await call.message.delete()
    except:
        await state.finish()
        await call.message.answer('Что-то пошло не так:(')
        await call.message.delete()
    else:
        if random_task[0] == '0':
            task = 'Задания кончились, можно ложиться спать!'
            await call.message.answer(text=task)
            await state.finish()
            await call.message.delete()
        else:
            photo = open(str(random_task[3]), 'rb')
            async with state.proxy() as dt:
                dt['id_task'] = random_task[0]
            await GetAndCheckINFO.next()
            btn = InlineKeyboardButton(text='Стоп', callback_data='stop')
            geti_btns = InlineKeyboardMarkup(row_width=1).add(btn)
            await bot.send_photo(call.message.chat.id, photo=photo,
                                 caption='Дробную часть от целой разделяй точкой!',
                                 reply_markup=geti_btns)
            await call.message.delete()


@dp.message_handler(state=GetAndCheckINFO.CHECK_ANSWER_INFO)
async def check_answer_info_random_task(message: types.Message,
                                        state: FSMContext):
    async with state.proxy() as dt:
        if data.check_answer(dt['id_task'], message.text, 'i' + str(message.chat.id), 'i_tasks'):
            btns = [
                InlineKeyboardButton(text='Вернуться в меню', callback_data='info_menu')
            ]
            kb = InlineKeyboardMarkup(row_width=1).add(*btns)
            await message.answer('Все верно! Молодчинка:)', reply_markup=kb)
            await state.finish()
        else:
            await message.answer('Пока неверно, попробуй еще разок')


@dp.callback_query_handler(text='getm')
async def get_task_math(call: types.CallbackQuery,
                        state: FSMContext):
    await GetAndCheckMATH.GET_TASK.set()
    try:
        random_task = data.get_random_not_done_task('m'
                                                    + str(call.message.chat.id),
                                                    'm_tasks')
    except OperationalError:
        btn = InlineKeyboardButton(text='Создать базу для математики',
                                   callback_data='create_math_base')
        kb = InlineKeyboardMarkup(row_width=1).add(btn)
        await state.finish()
        await call.message.answer('Таблица не создана'
                             + '\nСоздай базу',
                             reply_markup=kb)
        await call.message.delete()
    except:
        await state.finish()
        await call.message.answer('Что-то пошло не так:(')
        await call.message.delete()
    else:    
        if random_task[0] == '0':
            task = 'Задания кончились, можно ложиться спать!'
            await call.message.answer(task, reply_markup=ReplyKeyboardRemove())
            await state.finish()
            await call.message.delete()
        else:
            photo = open(str(random_task[3]), 'rb')
            async with state.proxy() as dt:
                dt['id_task'] = random_task[0]
            await GetAndCheckMATH.next()
            btn = InlineKeyboardButton(text='Стоп',
                                       callback_data='stop')
            getm_btns = InlineKeyboardMarkup(row_width=1).add(btn)
            await bot.send_photo(call.message.chat.id,
                                 photo=photo,
                                 caption='Дробную часть от целой отделяй точкой!',
                                 reply_markup=getm_btns)
            await call.message.delete()


@dp.message_handler(state=GetAndCheckMATH.CHECK_ANSWER_MATH)
async def check_answer_math_random_task(message: types.Message,
                                   state: FSMContext):
    async with state.proxy() as dt:
        if data.check_answer(dt['id_task'], message.text, 'm' + str(message.chat.id), 'm_tasks'):
            btns = [
                InlineKeyboardButton(text='Вернуться в меню', callback_data='math_menu')
            ]
            kb = InlineKeyboardMarkup(row_width=1).add(*btns)
            await message.answer('Все верно! Молодчинка:)', reply_markup=kb)
            await state.finish()
        else:
            await message.answer('Неверно!\nПопробуй ещё раз')


@dp.callback_query_handler(text='menu')
async def main_menu(call: types.CallbackQuery):
    btns = [
        InlineKeyboardButton(text='Математика', callback_data='math_menu'),
        InlineKeyboardButton(text='Информатика', callback_data='info_menu')
    ]
    kb = InlineKeyboardMarkup(row_width=1).add(*btns)
    await call.message.answer('Основное меню', reply_markup=kb)
    await call.message.delete()


@dp.callback_query_handler(text='math_menu')
async def math_menu(call: types.CallbackQuery):
    btns = [
        InlineKeyboardButton(text='Случайное задание', callback_data='getm'),
        InlineKeyboardButton(text='Вернуться', callback_data='menu')
    ]
    kb = InlineKeyboardMarkup(row_width=1).add(*btns)
    await call.message.answer('Основное меню математики', reply_markup=kb)
    await call.message.delete()


@dp.callback_query_handler(text='info_menu')
async def info_menu(call: types.CallbackQuery):
    btns = [
        InlineKeyboardButton(text='Случайное задание', callback_data='geti'),
        InlineKeyboardButton(text='Вернуться', callback_data='menu')
    ]
    kb = InlineKeyboardMarkup(row_width=1).add(*btns)
    await call.message.answer('Основное меню информатики', reply_markup=kb)
    await call.message.delete()


while __name__ == '__main__':
    executor.start_polling(dp)
