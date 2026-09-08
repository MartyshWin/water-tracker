from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class WaterLog(Base):
    __tablename__ = "water_logs"
    id = Column(Integer, primary_key=True)
    drink_type = Column(String, nullable=False)
    amount_ml = Column(Integer, nullable=False)
    hydration_factor = Column(Float, default=1.0)
    meal_relation = Column(String, nullable=True)   # before / after / none
    comment = Column(String, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())