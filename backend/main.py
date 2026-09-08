from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from contextlib import asynccontextmanager

from database import engine, Base, get_session
from models import WaterLog
from schemas import WaterLogCreate, WaterLogOut

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/api/logs", response_model=list[WaterLogOut])
async def list_logs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WaterLog).order_by(WaterLog.logged_at))
    return result.scalars().all()

@app.post("/api/logs", response_model=WaterLogOut)
async def add_log(payload: WaterLogCreate, session: AsyncSession = Depends(get_session)):
    log = WaterLog(**payload.model_dump())
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

# отдаёт frontend/index.html как статику
app.mount("/", StaticFiles(directory="/frontend", html=True), name="frontend")