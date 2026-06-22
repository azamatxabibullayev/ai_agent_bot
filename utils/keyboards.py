from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🛍 Buyurtma berish"),
        KeyboardButton(text="📦 Mahsulotlar"),
    )
    builder.row(
        KeyboardButton(text="📋 Mening buyurtmalarim"),
        KeyboardButton(text="ℹ️ Yordam"),
    )
    builder.row(
        KeyboardButton(text="🔄 Suhbatni tozalash"),
    )
    return builder.as_markup(resize_keyboard=True)


def contact_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📱 Raqamimni yuborish", request_contact=True))
    builder.row(KeyboardButton(text="◀️ Orqaga"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def confirm_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_order:{order_id}"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_order:{order_id}"),
    )
    return builder.as_markup()


def admin_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Qabul qilindi", callback_data=f"admin_confirm:{order_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_cancel:{order_id}"),
    )
    return builder.as_markup()


def back_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="◀️ Asosiy menyu"))
    return builder.as_markup(resize_keyboard=True)
