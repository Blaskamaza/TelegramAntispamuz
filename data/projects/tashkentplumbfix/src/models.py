from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

# --- DB Models (Pydantic representation) ---

class UserBase(BaseModel):
    telegram_id: int
    full_name: str
    role: Literal['client', 'master']
    phone: Optional[str] = None

class CreateRequest(BaseModel):
    description: str
    photo_url: Optional[str] = None

class RequestResponse(CreateRequest):
    id: UUID
    client_id: UUID
    status: str
    created_at: datetime

class CreateBid(BaseModel):
    request_id: UUID
    price: int
    message: Optional[str] = None

class BidResponse(CreateBid):
    id: UUID
    master_id: UUID
    status: str