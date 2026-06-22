from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.connection import AsyncSessionLocal
from database.crud import (
    get_or_create_user, get_available_products,
    get_conversation_history, save_message,
    create_order, get_user_orders, get_product_by_id,
    decrease_product_quantity, update_user_contact,
)
from ai.agent import AIAgent, format_products_for_ai
from utils.keyboards import (
    main_menu_keyboard, confirm_order_keyboard,
    admin_order_keyboard
)
from utils.helpers import (
    format_order_for_admin, format_order_for_user, ADMIN_ID
)

router = Router()
ai_agent = AIAgent()


@router.message(F.text == "📋 Mening buyurtmalarim")
@router.message(Command("myorders"))
async def my_orders(message: Message):
    async with AsyncSessionLocal() as session:
        orders = await get_user_orders(session, message.from_user.id)

    if not orders:
        await message.answer(
            "📋 Sizda hali buyurtma yo'q.\n"
            "Buyurtma berish uchun shunchaki yozing: <i>\"iPhone 15 kerak\"</i>",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard()
        )
        return

    text = "📋 <b>SIZNING BUYURTMALARINGIZ:</b>\n\n"
    for order in orders[:10]:  # oxirgi 10 ta
        text += format_order_for_user(order) + "\n\n"

    await message.answer(text, parse_mode="HTML", reply_markup=main_menu_keyboard())


@router.callback_query(F.data.startswith("confirm_order:"))
async def user_confirm_order(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        from database.models import Order, User
        from sqlalchemy import select
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            await callback.answer("Buyurtma topilmadi!", show_alert=True)
            return

        result2 = await session.execute(
            select(User).where(User.id == order.user_id)
        )
        user = result2.scalar_one_or_none()

        if order.product_id:
            await decrease_product_quantity(session, order.product_id, order.quantity)

        order.status = "pending"
        await session.commit()

        if ADMIN_ID:
            admin_text = format_order_for_admin(order, user)
            try:
                await bot.send_message(
                    ADMIN_ID,
                    f"🔔 <b>YANGI TASDIQLANGAN BUYURTMA!</b>\n\n{admin_text}",
                    parse_mode="HTML",
                    reply_markup=admin_order_keyboard(order.id)
                )
            except Exception as e:
                print(f"Admin ga xabar yuborishda xatolik: {e}")

    await callback.message.edit_text(
        f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"📦 {order.product_name}\n"
        f"🔢 Miqdor: {order.quantity} ta\n\n"
        f"Tez orada operator siz bilan bog'lanadi. 📞",
        parse_mode="HTML"
    )
    await callback.answer("Buyurtma tasdiqlandi! ✅")


@router.callback_query(F.data.startswith("cancel_order:"))
async def user_cancel_order(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        from database.models import Order
        from sqlalchemy import select
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.status = "cancelled"
            await session.commit()

    await callback.message.edit_text(
        "❌ Buyurtma bekor qilindi.\n\n"
        "Yana buyurtma bermoqchi bo'lsangiz, yozing!"
    )
    await callback.answer("Bekor qilindi")


@router.callback_query(F.data.startswith("admin_confirm:"))
async def admin_confirm_order(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        from database.models import Order, User
        from sqlalchemy import select
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.status = "confirmed"
            await session.commit()

            result2 = await session.execute(select(User).where(User.id == order.user_id))
            user = result2.scalar_one_or_none()
            if user:
                try:
                    await bot.send_message(
                        user.telegram_id,
                        f"🎉 <b>Xushxabar!</b>\n\n"
                        f"Sizning buyurtmangiz <b>#{order.id}</b> tasdiqlandi!\n"
                        f"📦 {order.product_name}\n\n"
                        f"Tez orada yetkazib beriladi. 🚚",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>ADMIN TOMONIDAN TASDIQLANDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("Tasdiqlandi ✅")


@router.callback_query(F.data.startswith("admin_cancel:"))
async def admin_cancel_order(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        from database.models import Order, User
        from sqlalchemy import select
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.status = "cancelled"
            await session.commit()

            result2 = await session.execute(select(User).where(User.id == order.user_id))
            user = result2.scalar_one_or_none()
            if user:
                try:
                    await bot.send_message(
                        user.telegram_id,
                        f"😔 Buyurtmangiz <b>#{order.id}</b> rad etildi.\n\n"
                        f"Boshqa mahsulot tanlash uchun yozing yoki operator bilan bog'laning.",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>ADMIN TOMONIDAN RAD ETILDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("Rad etildi ❌")


@router.message(F.text == "🛍 Buyurtma berish")
async def start_order(message: Message):
    await message.answer(
        "🛍 <b>Buyurtma berish</b>\n\n"
        "Qaysi mahsulot kerakligini yozing.\n"
        "Masalan:\n"
        "• <i>iPhone 15 kerak</i>\n"
        "• <i>256GB qora iPhone 15 Pro bor mi?</i>\n"
        "• <i>10 million atrofida telefon taklif qiling</i>\n\n"
        "AI assistant sizga yordam beradi! 🤖",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


@router.message(F.text & ~F.text.startswith("/"))
async def ai_chat_handler(message: Message, bot: Bot):
    skip_texts = {"📦 Mahsulotlar", "📋 Mening buyurtmalarim", "ℹ️ Yordam",
                  "🔄 Suhbatni tozalash", "🛍 Buyurtma berish", "◀️ Asosiy menyu"}
    if message.text in skip_texts:
        return

    await bot.send_chat_action(message.chat.id, "typing")

    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )

        products = await get_available_products(session)
        products_info = format_products_for_ai(products)

        history = await get_conversation_history(session, message.from_user.id, limit=15)
        history_dicts = [{"role": h.role, "message": h.message} for h in history]

        await save_message(session, message.from_user.id, "user", message.text)
        history_dicts.append({"role": "user", "message": message.text})

        ai_text, order_data = await ai_agent.get_response(
            user_message=message.text,
            conversation_history=history_dicts,
            products_info=products_info,
        )

        await save_message(session, message.from_user.id, "model", ai_text)

        if order_data and order_data.get("ready"):
            product_id = None
            product_name = order_data.get("product_name", "Noma'lum mahsulot")

            for p in products:
                if (p.model.lower() in product_name.lower() or
                        product_name.lower() in p.model.lower() or
                        p.name.lower() in product_name.lower()):
                    product_id = p.id
                    product_name = p.model
                    break

            order = await create_order(
                session=session,
                user_id=user.id,
                product_id=product_id,
                product_name=product_name,
                quantity=order_data.get("quantity", 1),
                customer_name=order_data.get("customer_name"),
                customer_phone=order_data.get("customer_phone"),
                customer_address=order_data.get("customer_address"),
                notes=order_data.get("summary"),
            )

            if order_data.get("customer_phone"):
                await update_user_contact(
                    session,
                    message.from_user.id,
                    phone_number=order_data.get("customer_phone"),
                    full_name=order_data.get("customer_name"),
                )

            await message.answer(ai_text, parse_mode="HTML", reply_markup=main_menu_keyboard())

            order_summary = (
                f"\n\n📋 <b>BUYURTMA MA'LUMOTLARI:</b>\n"
                f"📦 Mahsulot: {order.product_name}\n"
                f"🔢 Miqdor: {order.quantity} ta\n"
                f"👤 Ism: {order.customer_name or 'Ko-rsatilmagan'}\n"
                f"📱 Telefon: {order.customer_phone or 'Ko-rsatilmagan'}\n"
                f"📍 Manzil: {order.customer_address or 'Ko-rsatilmagan'}\n\n"
                f"Buyurtmani tasdiqlaymizmi?"
            )
            await message.answer(
                order_summary,
                parse_mode="HTML",
                reply_markup=confirm_order_keyboard(order.id)
            )
        else:
            await message.answer(
                ai_text,
                parse_mode="HTML",
                reply_markup=main_menu_keyboard()
            )
