from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    budget_limit = Column(Integer, nullable=True) # In USD or Millions SOM
    district_pref = Column(String, nullable=True) # e.g., 'Chilonzor'
    has_room = Column(Boolean, default=False) # True if offering, False if searching
    contact_username = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())