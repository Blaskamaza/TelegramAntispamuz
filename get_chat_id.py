"""
Временный скрипт для получения Chat ID группы
Запусти его вместо основного бота на 30 секунд
"""

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import os
from dotenv import load_dotenv

# Загрузить .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN не найден в .env!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

print("🔍 Скрипт запущен! Жду сообщения из группы...")
print("📝 Напиши ЛЮБОЕ сообщение в группе (например: test)")
print("")

@dp.message()
async def show_chat_id(message: Message):
    """Показать информацию о чате"""
    chat_id = message.chat.id
    chat_type = message.chat.type
    chat_title = message.chat.title or "Без названия"
    
    print("=" * 50)
    print(f"📊 ИНФОРМАЦИЯ О ЧАТЕ:")
    print(f"   Название: {chat_title}")
    print(f"   Chat ID: {chat_id}")
    print(f"   Тип: {chat_type}")
    print("=" * 50)
    print("")
    print(f"✅ Используй этот ID в .env:")
    print(f"   GROUPS_MAIN={chat_id}")
    print("")
    
    # Остановить после первого сообщения
    await dp.stop_polling()

async def main():
    try:
        print("✅ Бот подключился к Telegram!")
        print("⏳ Жду сообщения из группы...")
        print("")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n❌ Остановлено пользователем")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
