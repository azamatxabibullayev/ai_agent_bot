import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from database.connection import init_db, close_db
from database.crud import seed_products
from database.connection import AsyncSessionLocal
from handlers.start import router as start_router
from handlers.orders import router as orders_router
from handlers.admin import router as admin_router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    logger.info("🚀 Bot ishga tushmoqda...")

    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_products(session)

    if ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                "🟢 <b>AI Agent Bot ishga tushdi!</b>\n\n"
                "Bot muvaffaqiyatli ishga tushirildi va buyurtma qabul qilishga tayyor.\n\n"
                "/admin — Admin panel",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Admin ga xabar yuborishda xatolik: {e}")

    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")


async def on_shutdown(bot: Bot):
    logger.info("🛑 Bot to'xtatilmoqda...")
    await close_db()

    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, "🔴 Bot to'xtatildi.")
        except Exception:
            pass

    logger.info("✅ Bot to'xtatildi.")


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi! .env faylni tekshiring.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(orders_router)

    logger.info("🤖 Polling boshlanmoqda...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
