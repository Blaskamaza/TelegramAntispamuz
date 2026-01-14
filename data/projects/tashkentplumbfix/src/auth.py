from fastapi import Header, HTTPException, Depends
import json
import hashlib
import hmac
from urllib.parse import parse_qsl
from src.config import settings
from src.database import supabase

# Simple mock for MVP. 
# In production: Verify hmac of init_data sent from Telegram WebApp.

async def get_current_user(x_telegram_init_data: str = Header(None)):
    """
    Decodes Telegram WebApp InitData to identify the user.
    For this MVP code, we assume the frontend sends a raw JSON object string of the user
    in a header for simplicity (INSECURE - DO NOT USE IN PROD).
    
    PROD: Validate hash(init_data) == HMAC_SHA256(bot_token).
    """
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing Auth Header")
    
    try:
        # Expecting {"id": 12345, "first_name": "Aziz"} in header for MVP testing
        tg_user = json.loads(x_telegram_init_data)
        
        # Fetch or create user in DB
        response = supabase.table("users").select("*").eq("telegram_id", tg_user['id']).execute()
        
        if not response.data:
            # Auto-register if not exists (Default to client, user can switch later)
            new_user = {
                "telegram_id": tg_user['id'],
                "full_name": tg_user.get('first_name', 'Unknown'),
                "role": "client"
            }
            res = supabase.table("users").insert(new_user).execute()
            return res.data[0]
            
        return response.data[0]
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Auth: {str(e)}")