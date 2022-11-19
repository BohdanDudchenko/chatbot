import json
import random
import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
import messages as s_msg
import keyboards as nav
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from States import Order

logging.basicConfig(level=logging.INFO)

with open("config.json", "r", encoding="utf-8") as file:
    cfg = json.loads(file.read())
    token = cfg[0]["token"]
    admin = cfg[0]["admin"]

storage = MemoryStorage()
bot = Bot(token)
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()



@dp.message_handler(commands="start")
async def text(msg: types.Message):
    user = cursor.execute('SELECT * FROM users where user_id=?', (msg.from_user.id, )).fetchone()
    if user is None:
        await bot.send_message(msg.from_user.id, text=s_msg.welcome, reply_markup=nav.main_menu())
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (msg.from_user.id, ))
        conn.commit()
    else:
        await bot.send_message(msg.from_user.id, text=s_msg.already_user, reply_markup=nav.main_menu())


@dp.message_handler(content_types='text')
async def text(msg: types.Message):
    if msg.text == nav.information:
        await bot.send_message(msg.from_user.id, text=s_msg.information, reply_markup=nav.main_menu())
    elif msg.text == nav.make_an_order:
        await bot.send_message(msg.from_user.id, text=s_msg.select, reply_markup=nav.make_order())
    elif msg.text == nav.terms:
        await bot.send_message(msg.from_user.id, text=s_msg.terms, reply_markup=nav.main_menu())


@dp.callback_query_handler(text_contains="orderinfo/")
async def text(call: types.CallbackQuery):
    data = call.data
    info = data.split("/")
    ticket_number = random.randint(8383, 939299929)
    type1 = info[1]
    type2 = info[2]
    price = info[3]
    count_tickets = cursor.execute("SELECT count_tickets FROM users WHERE user_id=?", (call.from_user.id, )).fetchone()[0]
    if count_tickets < 3:
        cursor.execute("UPDATE users SET count_tickets = count_tickets + 1 WHERE user_id=?", (call.from_user.id, ))
        cursor.execute("INSERT INTO tickets (user_id, ticket_number, type1, type2, price) VALUES (?, ?, ?, ?, ?);", (call.from_user.id, ticket_number, type1, type2, price, ))
        conn.commit()
        await call.message.edit_text(s_msg.tiket_sent)

        # отправка сообщения админу
        await bot.send_message(admin, text=s_msg.admin_chat.format(ticket_number, type1, type2, price), reply_markup=nav.send_message_admin(ticket_number))
    else:
        await call.message.edit_text(s_msg.limit)


@dp.callback_query_handler(text_contains="send/answer/")
async def text(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    info = data.split("/")
    who = info[2]
    ticket_id = info[3]
    data = cursor.execute("SELECT ticket_number FROM tickets WHERE ticket_number=?;", (ticket_id, )).fetchone()
    if data is None:
        await call.message.edit_text(call.from_user.id, text="Этот заказ уже выполнен!")

    else:
        async with state.proxy() as data:
            data['ticket_id'] = ticket_id
            data['who'] = who
            data['call'] = call
            await Order.message.set()
            await call.message.edit_text(text="Введите ваше сообщение!")


@dp.message_handler(state=Order.message)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message'] = message.text
        if data['who'] == 'admin':
            user_id = cursor.execute("SELECT user_id FROM tickets WHERE ticket_number=?", (data["ticket_id"],)).fetchone()[0]
            await bot.send_message(user_id, text=data["message"], reply_markup=nav.send_message_user(data['ticket_id']))
            await message.delete()
        else:
            await bot.send_message(admin, text=data["message"], reply_markup=nav.send_message_admin(data['ticket_id']))
            await message.delete()
        await data['call'].message.delete()
        await bot.send_message(data['call'].from_user.id, f"Заказ номер: {data['ticket_id']}\nОтправлено: {data['message']}")
        await state.finish()


@dp.callback_query_handler(text_contains="COMPLETED/")
async def text(call: types.CallbackQuery):
    try:
        data = call.data
        info = data.split("/")
        ticket_id = info[1]
        user_id = cursor.execute("SELECT user_id FROM tickets WHERE ticket_number=?", (ticket_id,)).fetchone()[0]
        cursor.execute("DELETE FROM tickets WHERE ticket_number=?;", (ticket_id, ))
        cursor.execute("UPDATE users SET count_tickets = count_tickets - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        await call.message.edit_text(text=f"Заказ № {ticket_id} успешно завершён и удалён с базы данных.")
        await bot.send_message(user_id, text=f"Заказ № {ticket_id} выполнен!.")
    except TypeError:
        await call.message.edit_text(text=f"Такого заказа уже нет в базе!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)