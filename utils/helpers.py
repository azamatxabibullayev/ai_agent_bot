import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


def format_order_for_admin(order, user) -> str:
    return (
        f"🛒 <b>YANGI BUYURTMA #{order.id}</b>\n\n"
        f"👤 <b>Mijoz:</b> {order.customer_name or user.full_name or 'Noma-lum'}\n"
        f"📱 <b>Telefon:</b> {order.customer_phone or user.phone_number or 'Ko-rsatilmagan'}\n"
        f"📍 <b>Manzil:</b> {order.customer_address or 'Ko-rsatilmagan'}\n\n"
        f"📦 <b>Mahsulot:</b> {order.product_name}\n"
        f"🔢 <b>Miqdor:</b> {order.quantity} ta\n\n"
        f"💬 <b>Telegram:</b> @{user.username or 'yo-q'} (ID: {user.telegram_id})\n"
        f"📝 <b>Izoh:</b> {order.notes or 'Yo-q'}\n\n"
        f"⏰ <b>Vaqt:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}"
    )


def format_order_for_user(order) -> str:
    status_map = {
        "pending": "⏳ Kutilmoqda",
        "confirmed": "✅ Tasdiqlangan",
        "cancelled": "❌ Bekor qilingan",
    }
    status = status_map.get(order.status, order.status)

    return (
        f"🛒 <b>Buyurtma #{order.id}</b>\n"
        f"📦 {order.product_name}\n"
        f"🔢 Miqdor: {order.quantity} ta\n"
        f"📊 Status: {status}\n"
        f"⏰ {order.created_at.strftime('%d.%m.%Y %H:%M')}"
    )


def format_product_list(products) -> str:
    if not products:
        return "😔 Hozirda omborda mahsulot yo'q."

    lines = ["📱 <b>MAVJUD MAHSULOTLAR:</b>\n"]
    current_name = None

    for p in sorted(products, key=lambda x: (x.name, x.storage or "", x.color or "")):
        if p.name != current_name:
            if current_name is not None:
                lines.append("")
            lines.append(f"<b>📱 {p.name}</b>")
            current_name = p.name

        lines.append(
            f"  • {p.storage or ''} {p.color or ''} — "
            f"<b>{p.price:,.0f} so'm</b> "
            f"({'mavjud' if p.quantity > 0 else 'tugagan'}: {p.quantity} ta)"
        )

    return "\n".join(lines)