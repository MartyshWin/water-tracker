from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database import engine, Base, get_session
from models import User, DrinkType, WaterLog
from schemas import DrinkTypeOut, WaterLogCreate, WaterLogOut

# Пресеты справочника напитков — заводятся один раз при первом старте.
DEFAULT_DRINK_TYPES = [
    {"name": "Вода", "hydration_factor": 1.0, "icon": "💧"},
    {"name": "Чай", "hydration_factor": 0.9, "icon": "🍵"},
    {"name": "Кофе", "hydration_factor": 0.75, "icon": "☕"},
    {"name": "Сок", "hydration_factor": 0.9, "icon": "🧃"},
]

# Пока нет Telegram-авторизации — все записи идут от одного dev-юзера.
DEV_TELEGRAM_ID = "dev-user"


async def get_or_create_dev_user(session: AsyncSession) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == DEV_TELEGRAM_ID)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=DEV_TELEGRAM_ID)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        result = await session.execute(select(DrinkType))
        if result.scalars().first() is None:
            for dt in DEFAULT_DRINK_TYPES:
                session.add(DrinkType(**dt))
            await session.commit()

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/drink-types", response_model=list[DrinkTypeOut])
async def list_drink_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(DrinkType))
    return result.scalars().all()


@app.get("/api/logs", response_model=list[WaterLogOut])
async def list_logs(session: AsyncSession = Depends(get_session)):
    user = await get_or_create_dev_user(session)
    result = await session.execute(
        select(WaterLog)
        .where(WaterLog.user_id == user.id)
        .order_by(WaterLog.logged_at)
    )
    return result.scalars().all()


@app.post("/api/logs", response_model=WaterLogOut)
async def add_log(payload: WaterLogCreate, session: AsyncSession = Depends(get_session)):
    user = await get_or_create_dev_user(session)
    log = WaterLog(user_id=user.id, **payload.model_dump())
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


@app.delete("/api/logs/{log_id}")
async def delete_log(log_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(delete(WaterLog).where(WaterLog.id == log_id))
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(404, "not found")
    return {"ok": True}


app.mount("/", StaticFiles(directory="/frontend", html=True), name="frontend")