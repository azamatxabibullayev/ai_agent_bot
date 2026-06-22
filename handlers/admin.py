from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.connection import AsyncSessionLocal
from database.crud import get_available_products, seed_products
from database.models import Order, User, Product
from utils.helpers import ADMIN_ID, format_product_list
from sqlalchemy import select, func

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🔧 <b>ADMIN PANEL</b>\n\n"
        "/stats — Statistika\n"
        "/all_orders — Barcha buyurtmalar\n"
        "/seed — Test ma'lumotlarini qo'shish\n"
        "/broadcast — Barcha userlarga xabar",
        parse_mode="HTML"
    )


@router.message(Command("stats"))
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as session:
        orders_result = await session.execute(select(func.count(Order.id)))
        total_orders = orders_result.scalar()

        pending_result = await session.execute(
            select(func.count(Order.id)).where(Order.status == "pending")
        )
        pending_orders = pending_result.scalar()

        confirmed_result = await session.execute(
            select(func.count(Order.id)).where(Order.status == "confirmed")
        )
        confirmed_orders = confirmed_result.scalar()

        users_result = await session.execute(select(func.count(User.id)))
        total_users = users_result.scalar()

        products_result = await session.execute(
            select(func.sum(Product.quantity)).where(Product.is_available == True)
        )
        total_stock = products_result.scalar() or 0

    await message.answer(
        f"📊 <b>STATISTIKA</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n\n"
        f"🛒 Jami buyurtmalar: <b>{total_orders}</b>\n"
        f"⏳ Kutilayotgan: <b>{pending_orders}</b>\n"
        f"✅ Tasdiqlangan: <b>{confirmed_orders}</b>\n\n"
        f"📦 Ombordagi mahsulotlar: <b>{total_stock} ta</b>",
        parse_mode="HTML"
    )


@router.message(Command("all_orders"))
async def all_orders(message: Message):
    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order).order_by(Order.created_at.desc()).limit(20)
        )
        orders = result.scalars().all()

    if not orders:
        await message.answer("Hali buyurtma yo'q.")
        return

    text = "📋 <b>OXIRGI 20 TA BUYURTMA:</b>\n\n"
    for order in orders:
        status_emoji = {"pending": "⏳", "confirmed": "✅", "cancelled": "❌"}.get(order.status, "❓")
        text += (
            f"{status_emoji} #{order.id} — {order.product_name} "
            f"({order.quantity}ta) — {order.customer_name or "Noma\'lum"}\n"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("seed"))
async def seed_data(message: Message):
    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as session:
        await seed_products(session)

    await message.answer("✅ Test mahsulotlar qo'shildi!")


@router.message(Command("products_admin"))
async def admin_products(message: Message):
    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as session:
        products = await get_available_products(session)

    text = format_product_list(products)
    await message.answer(text, parse_mode="HTML")
