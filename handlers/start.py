from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database.connection import AsyncSessionLocal
from database.crud import (
    get_or_create_user, get_available_products,
    clear_conversation_history
)
from utils.keyboards import main_menu_keyboard, back_keyboard
from utils.helpers import format_product_list

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )

    await message.answer(
        f"👋 Salom, <b>{message.from_user.first_name}</b>!\n\n"
        f"🤖 Men <b>TechShop AI Assistenti</b>man.\n"
        f"Sizga telefon va texnika buyurtma berishda yordam beraman.\n\n"
        f"📱 Nima xizmat? Shunchaki yozing — men tushunarman!\n"
        f"Masalan: <i>\"iPhone 15 kerak\"</i> yoki <i>\"eng arzon telefon qaysi?\"</i>",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text == "ℹ️ Yordam")
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>BOT HAQIDA MA'LUMOT</b>\n\n"
        "Bu AI-powered savdo assistenti. Men sizga:\n\n"
        "✅ Mavjud telefonlar haqida ma'lumot beraman\n"
        "✅ Mos variantni taklif qilaman\n"
        "✅ Buyurtma qabul qilaman\n"
        "✅ Yetkazib berish uchun ma'lumot yig'aman\n\n"
        "<b>Buyruqlar:</b>\n"
        "/start — Botni qayta ishga tushirish\n"
        "/products — Barcha mahsulotlar\n"
        "/myorders — Mening buyurtmalarim\n"
        "/clear — Suhbatni tozalash\n\n"
        "💬 Shunchaki xabar yozing — AI sizga yordam beradi!",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


@router.message(F.text == "📦 Mahsulotlar")
@router.message(Command("products"))
async def show_products(message: Message):
    async with AsyncSessionLocal() as session:
        products = await get_available_products(session)

    text = format_product_list(products)
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


@router.message(F.text == "🔄 Suhbatni tozalash")
@router.message(Command("clear"))
async def clear_chat(message: Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        await clear_conversation_history(session, message.from_user.id)

    await message.answer(
        "🔄 Suhbat tarixi tozalandi. Yangi suhbat boshlashingiz mumkin!",
        reply_markup=main_menu_keyboard()
    )
