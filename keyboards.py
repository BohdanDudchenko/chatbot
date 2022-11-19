import sqlite3
from itertools import groupby


from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


information = 'Информация'
make_an_order = 'Сделать заказ'
terms = 'Условия'


archive_soft_price = '350'
video_soft_price = '250'
preview_soft_price = '100'

archive_game_price = '350'
video_game_price = '250'
preview_game_price = '100'

upload_video_price = '100'
seo_price = '150'


def main_menu():
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(make_an_order)
    menu.row(information, terms)
    return menu


def make_order():
    menu = InlineKeyboardMarkup(row_width=1)
    archive_soft = InlineKeyboardButton(text="Архив (soft) - 350р", callback_data=f"orderinfo/archive/soft/{archive_soft_price}")
    video_soft = InlineKeyboardButton(text="Видео (soft) - 250р", callback_data=f"orderinfo/video/soft/{video_soft_price}")
    preview_soft = InlineKeyboardButton(text="Превью (soft) - 100р", callback_data=f"orderinfo/preview/soft/{preview_soft_price}")
    archive_game = InlineKeyboardButton(text="Aрхив (game) - 350р", callback_data=f"orderinfo/archive/game/{archive_game_price}")
    video_game = InlineKeyboardButton(text="Видео (game) - 250р", callback_data=f"orderinfo/video/game/{video_game_price}")
    preview_game = InlineKeyboardButton(text="Превью (game) - 100р", callback_data=f"orderinfo/preview/game/{preview_game_price}")
    upload_video = InlineKeyboardButton(text="Залив видео - 100р", callback_data=f"orderinfo/upload/video/{upload_video_price}")
    seo = InlineKeyboardButton(text="Накрутка SEO - 150р", callback_data=f"orderinfo/seo/seo/{seo_price}")

    menu.add(archive_soft)
    menu.add(video_soft)
    menu.add(preview_soft)
    menu.add(archive_game)
    menu.add(video_game)
    menu.add(preview_game)
    menu.add(upload_video)
    menu.add(seo)

    return menu


def send_message_admin(ticket_number):
    menu = InlineKeyboardMarkup(row_width=1)
    send_answer = InlineKeyboardButton(text=f"Ответить на заказ!", callback_data=f"send/answer/admin/{ticket_number}")
    order_completed = InlineKeyboardButton(text="Заказ выполнен!", callback_data=f"COMPLETED/{ticket_number}")
    menu.add(send_answer)
    menu.add(order_completed)
    return menu


def send_message_user(ticket_number):
    menu = InlineKeyboardMarkup(row_width=1)
    send_answer = InlineKeyboardButton(text=f"Написать", callback_data=f"send/answer/user/{ticket_number}")
    menu.add(send_answer)
    return menu