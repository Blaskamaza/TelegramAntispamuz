from fastapi import FastAPI, Request
from aiogram.types import Update
from src.bot import bot, dp
from src.config import settings
import uvicorn

app = FastAPI(title="InglizchaAI Backend")

@app.on_event("startup")
async def on_startup():
    # Set webhook on startup
    webhook_url = f"{settings.WEBHOOK_URL}/api/webhook/telegram"
    await bot.set_webhook(webhook_url)
    print(f"Webhook set to {webhook_url}")

@app.post("/api/webhook/telegram")
async def telegram_webhook(request: Request):
    update_data = await request.json()
    update = Update(**update_data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/")
async def health_check():
    return {"status": "InglizchaAI is live", "version": "MVP-1.0"}

# Local development entry point
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)