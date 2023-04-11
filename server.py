import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup
from google_sheets import Spreadsheet

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
spreadsheets = Spreadsheet()


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="/get_sheets"),
            types.KeyboardButton(text="/give_me_id"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Choose command"
    )

    answer = '<b>Hello! \n\nMy commands:\n\n /create [doc_name]\n\n/set_spreadsheet_id\n\n' \
             '/read Sheets1!A1:C3 (or another range)\n\n/get_sheets</b>'
    await message.answer(answer, reply_markup=keyboard, parse_mode='HTML')


@dp.callback_query_handler(text='/give_me_id')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    your_id = spreadsheets.give_me_id()
    await bot.send_message(callback_query.from_user.id, your_id, parse_mode='HTML')


@dp.message_handler(commands=['give_me_id'])
async def process_callback_button1(message: types.Message):
    your_id = spreadsheets.give_me_id()
    await message.answer(your_id, parse_mode='HTML')


@dp.message_handler(lambda message: message.text.startswith('/create'))
async def create_spreadsheet(message: types.Message):
    name = message.text[7:]
    link = spreadsheets.create_spreadsheet(name)
    answer_message = f"I created!\n\nHere's the link: {link}"

    builder = InlineKeyboardMarkup()
    builder.add(types.InlineKeyboardButton(
        text="give me id",
        callback_data="/give_me_id")
    )
    await message.answer(
        answer_message, reply_markup=builder, parse_mode="HTML")


@dp.message_handler(lambda message: message.text.startswith('/set_spreadsheet_id'))
async def set_spreadsheet_id(message: types.Message):
    spreadsheet_id = message.text[19:].strip()
    spreadsheets.set_spreadsheet_id(spreadsheet_id)
    answer_message = 'You set new spreadsheet id.'
    await message.answer(answer_message)


@dp.message_handler(commands=['get_sheets'])
async def get_sheets(message: types.Message):
    info = spreadsheets.get_list_of_sheets()
    answer_message = f"Here's the answer:\n\n{info}"
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/read'))
async def read_data(message: types.Message):
    range_values = message.text[5:].strip()
    answer = spreadsheets.read_the_spreadsheet(range_values)
    await message.answer(answer)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
