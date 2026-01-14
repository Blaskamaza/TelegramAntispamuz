from supabase import create_client, Client
from src.config import settings
import asyncio

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

async def get_or_create_user(tg_user):
    """Upsert user into Supabase"""
    data = {
        "telegram_id": tg_user.id,
        "full_name": tg_user.full_name,
        "username": tg_user.username
    }
    # Using upsert to handle existence check efficiently
    try:
        response = supabase.table("users").upsert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"DB Error: {e}")
        return None

async def add_xp(user_id: int, amount: int):
    """Increment XP for gamification"""
    # Note: In a real RPC, this would be an atomic SQL function
    try:
        user = supabase.table("users").select("xp_points").eq("telegram_id", user_id).execute()
        if user.data:
            current_xp = user.data[0]['xp_points']
            supabase.table("users").update({"xp_points": current_xp + amount}).eq("telegram_id", user_id).execute()
    except Exception as e:
        print(f"XP Error: {e}")

async def log_conversation(user_id, user_text, corrected, ai_resp):
    try:
        supabase.table("learning_logs").insert({
            "user_id": user_id,
            "user_text": user_text,
            "corrected_text": corrected,
            "ai_response": ai_resp
        }).execute()
    except Exception as e:
        print(f"Log Error: {e}")