from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime

class UserBase(SQLModel):
    username: Optional[str] = None
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    budget_min: int = 0
    budget_max: int = 0
    district_pref: Optional[str] = None
    habits: List[str] = Field(default=[], sa_column=Column(JSON))
    is_searching: bool = True

class User(UserBase, table=True):
    __tablename__ = "users"
    telegram_id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    telegram_id: int

class UserUpdate(UserBase):
    pass