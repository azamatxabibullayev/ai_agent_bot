from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from database.models import Product, User, Order, Conversation
from typing import Optional, List
from datetime import datetime


async def get_all_products(session: AsyncSession) -> List[Product]:
    result = await session.execute(
        select(Product).where(Product.is_available == True).order_by(Product.name)
    )
    return result.scalars().all()


async def get_available_products(session: AsyncSession) -> List[Product]:
    result = await session.execute(
        select(Product).where(
            and_(Product.is_available == True, Product.quantity > 0)
        ).order_by(Product.name)
    )
    return result.scalars().all()


async def search_products(session: AsyncSession, query: str) -> List[Product]:
    search = f"%{query.lower()}%"
    result = await session.execute(
        select(Product).where(
            and_(
                Product.is_available == True,
                Product.quantity > 0,
            )
        )
    )
    all_products = result.scalars().all()
    filtered = [
        p for p in all_products
        if query.lower() in p.name.lower()
           or query.lower() in p.model.lower()
           or (p.color and query.lower() in p.color.lower())
           or (p.storage and query.lower() in p.storage.lower())
    ]
    return filtered


async def get_product_by_id(session: AsyncSession, product_id: int) -> Optional[Product]:
    result = await session.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def decrease_product_quantity(session: AsyncSession, product_id: int, qty: int = 1) -> bool:
    product = await get_product_by_id(session, product_id)
    if product and product.quantity >= qty:
        product.quantity -= qty
        if product.quantity == 0:
            product.is_available = False
        product.updated_at = datetime.utcnow()
        await session.commit()
        return True
    return False


async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def update_user_contact(
        session: AsyncSession,
        telegram_id: int,
        phone_number: Optional[str] = None,
        address: Optional[str] = None,
        full_name: Optional[str] = None,
) -> Optional[User]:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        if phone_number:
            user.phone_number = phone_number
        if address:
            user.address = address
        if full_name:
            user.full_name = full_name
        user.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(user)
    return user


async def create_order(
        session: AsyncSession,
        user_id: int,
        product_id: Optional[int],
        product_name: str,
        quantity: int = 1,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        customer_address: Optional[str] = None,
        notes: Optional[str] = None,
) -> Order:
    order = Order(
        user_id=user_id,
        product_id=product_id,
        product_name=product_name,
        quantity=quantity,
        status="pending",
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_address=customer_address,
        notes=notes,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def get_order_by_id(session: AsyncSession, order_id: int) -> Optional[Order]:
    result = await session.execute(
        select(Order)
        .options(selectinload(Order.user), selectinload(Order.product))
        .where(Order.id == order_id)
    )
    return result.scalar_one_or_none()


async def get_user_orders(session: AsyncSession, telegram_id: int) -> List[Order]:
    result = await session.execute(
        select(Order)
        .join(User)
        .options(selectinload(Order.product))
        .where(User.telegram_id == telegram_id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


async def save_message(
        session: AsyncSession,
        telegram_id: int,
        role: str,
        message: str,
):
    conv = Conversation(
        telegram_id=telegram_id,
        role=role,
        message=message,
    )
    session.add(conv)
    await session.commit()


async def get_conversation_history(
        session: AsyncSession,
        telegram_id: int,
        limit: int = 20,
) -> List[Conversation]:
    result = await session.execute(
        select(Conversation)
        .where(Conversation.telegram_id == telegram_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return list(reversed(messages))


async def clear_conversation_history(session: AsyncSession, telegram_id: int):
    result = await session.execute(
        select(Conversation).where(Conversation.telegram_id == telegram_id)
    )
    convs = result.scalars().all()
    for conv in convs:
        await session.delete(conv)
    await session.commit()


async def seed_products(session: AsyncSession):
    result = await session.execute(select(Product))
    existing = result.scalars().first()
    if existing:
        return

    products = [
        Product(name="iPhone 15", model="iPhone 15 128GB", color="Black", storage="128GB",
                price=12500000, quantity=5, description="Apple iPhone 15, 128GB, qora rang"),
        Product(name="iPhone 15", model="iPhone 15 128GB", color="Blue", storage="128GB",
                price=12500000, quantity=3, description="Apple iPhone 15, 128GB, ko'k rang"),
        Product(name="iPhone 15", model="iPhone 15 256GB", color="Black", storage="256GB",
                price=14500000, quantity=2, description="Apple iPhone 15, 256GB, qora rang"),
        Product(name="iPhone 15 Pro", model="iPhone 15 Pro 256GB", color="Titanium", storage="256GB",
                price=18000000, quantity=4, description="Apple iPhone 15 Pro, 256GB, titanium rang"),
        Product(name="iPhone 15 Pro", model="iPhone 15 Pro 512GB", color="Black", storage="512GB",
                price=22000000, quantity=2, description="Apple iPhone 15 Pro, 512GB, qora rang"),
        Product(name="iPhone 15 Pro Max", model="iPhone 15 Pro Max 256GB", color="Titanium", storage="256GB",
                price=24000000, quantity=3, description="Apple iPhone 15 Pro Max, 256GB"),
        Product(name="iPhone 14", model="iPhone 14 128GB", color="Purple", storage="128GB",
                price=9500000, quantity=6, description="Apple iPhone 14, 128GB, binafsha"),
        Product(name="iPhone 14 Pro", model="iPhone 14 Pro 256GB", color="Gold", storage="256GB",
                price=15000000, quantity=2, description="Apple iPhone 14 Pro, 256GB, oltin"),
        Product(name="Samsung Galaxy S24", model="Samsung Galaxy S24 256GB", color="Black", storage="256GB",
                price=11000000, quantity=4, description="Samsung Galaxy S24, 256GB, qora"),
        Product(name="Samsung Galaxy S24 Ultra", model="Samsung Galaxy S24 Ultra 512GB", color="Titanium",
                storage="512GB",
                price=20000000, quantity=2, description="Samsung Galaxy S24 Ultra, 512GB"),
    ]

    for product in products:
        session.add(product)
    await session.commit()
    print("✅ Seed products added successfully")
