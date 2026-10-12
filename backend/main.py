from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database import engine, Base, get_session
from models import User, DrinkType, WaterLog
from schemas import DrinkTypeOut, WaterLogCreate, WaterLogOut, UserUpdate
from schemas.user import UserOut

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


# ---------- Water logs ----------

@app.get(
    "/api/water-logs",
    response_model=list[WaterLogOut],
    status_code=status.HTTP_200_OK,
    tags=["water-logs"],
    summary="Get a water log entry",
    responses={404: {"description": "Water Logs not found"}}
)
async def list_logs(session: AsyncSession = Depends(get_session)):
    user = await get_or_create_dev_user(session)
    result = await session.execute(
        select(WaterLog)
        .where(WaterLog.user_id == user.id)
        .order_by(WaterLog.logged_at)
    )
    return result.scalars().all()


@app.post(
    "/api/water-logs",
    response_model=WaterLogOut,
    status_code=status.HTTP_201_CREATED,
    tags=["water-logs"],
    summary="Add a water log entry",
    responses={404: {"description": "Drink type not found"}}
)
async def add_log(payload: WaterLogCreate, session: AsyncSession = Depends(get_session)):
    user = await get_or_create_dev_user(session)
    log = WaterLog(user_id=user.id, **payload.model_dump())
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log

@app.patch(
    "/api/profile",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    tags=["water-logs"],
    summary="Update a water log entry",
    responses={404: {"description": "Water Logs not found"}}
)
async def update_profile(payload: UserUpdate, session: AsyncSession = Depends(get_session)):
    user = await get_or_create_dev_user(session)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await session.commit()
    await session.refresh(user)
    return user

@app.delete(
    "/api/water-logs/{log_id}",
    status_code=status.HTTP_200_OK,
    tags=["water-logs"],
    summary="Delete a water log entry",
    responses={404: {"description": "Water Logs not found"}}
)
async def delete_log(log_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(delete(WaterLog).where(WaterLog.id == log_id))
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Water log not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------- Drink Types ----------

@app.get("/api/drink-types", response_model=list[DrinkTypeOut])
async def list_drink_types(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(DrinkType))
    return result.scalars().all()

# ---------- Main Path ----------

app.mount("/", StaticFiles(directory="/frontend", html=True), name="frontend")