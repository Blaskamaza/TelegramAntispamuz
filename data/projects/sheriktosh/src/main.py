from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from contextlib import asynccontextmanager
from src.config import settings
from src.bot_logic import router
from src.database import init_db

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    if settings.WEBHOOK_URL:
        await bot.set_webhook(settings.WEBHOOK_URL)
    yield
    # Shutdown
    await bot.delete_webhook()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook_handler(request: Request):
    update = types.Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {}

@app.get("/health")
async def health():
    return {"status": "ok"}