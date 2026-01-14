from fastapi import FastAPI, Depends, HTTPException, Header
from sqlmodel import Session, select, col
from contextlib import asynccontextmanager
from typing import List

from src.database import init_db, get_session
from src.models import User, UserUpdate
from src.utils import validate_telegram_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Hamxona API", lifespan=lifespan)

# --- Dependencies ---
def get_current_user_id(authorization: str = Header(None)) -> int:
    """Extracts Telegram ID from initData sent in Authorization header"""
    user_data = validate_telegram_data(authorization)
    return int(user_data['id'])

# --- Endpoints ---

@app.get("/api/v1/users/me", response_model=User)
def get_my_profile(user_id: int = Depends(get_current_user_id), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        # Auto-create entry if first time login, but return empty profile structure
        # In real app, we might redirect to onboarding
        raise HTTPException(status_code=404, detail="User not found, please register")
    return user

@app.post("/api/v1/users/me", response_model=User)
def create_or_update_profile(
    user_data: UserUpdate,
    authorization: str = Header(None),
    session: Session = Depends(get_session)
):
    tg_user = validate_telegram_data(authorization)
    user_id = tg_user['id']
    
    existing_user = session.get(User, user_id)
    if existing_user:
        user_data_dict = user_data.model_dump(exclude_unset=True)
        for key, value in user_data_dict.items():
            setattr(existing_user, key, value)
        session.add(existing_user)
        session.commit()
        session.refresh(existing_user)
        return existing_user
    else:
        # Create new
        new_user = User(telegram_id=user_id, **user_data.model_dump())
        # Fill defaults from Telegram if missing
        if not new_user.full_name:
            new_user.full_name = f"{tg_user.get('first_name', '')} {tg_user.get('last_name', '')}".strip()
        if not new_user.username:
            new_user.username = tg_user.get('username')
            
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

@app.get("/api/v1/matches/candidates", response_model=List[User])
def find_candidates(user_id: int = Depends(get_current_user_id), session: Session = Depends(get_session)):
    """
    Simple algorithm: Find people within budget range & same district.
    Exclude self.
    """
    me = session.get(User, user_id)
    if not me:
        raise HTTPException(status_code=400, detail="Complete your profile first")

    # Logic: Candidate's budget max must be >= my budget min
    statement = select(User).where(
        User.telegram_id != user_id,
        User.is_searching == True,
        User.budget_max >= me.budget_min,
        User.budget_min <= me.budget_max
    )
    
    if me.district_pref:
        statement = statement.where(User.district_pref == me.district_pref)
        
    results = session.exec(statement.limit(20)).all()
    return results