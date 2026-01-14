from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
import io
from src.config import settings
from src.ai_engine import transcribe_audio, get_tutor_response, text_to_speech
from src.database import get_or_create_user, add_xp, log_conversation

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await get_or_create_user(message.from_user)
    await message.answer(
        "🇺🇿 Salom! Men InglizchaAI man.\n🇬🇧 Hi! I am InglizchaAI. Send me a voice message to start practicing!"
    )

@dp.message(F.voice)
async def handle_voice(message: types.Message):
    user_id = message.from_user.id
    
    # 1. Feedback to user
    processing_msg = await message.answer("🎧 Listening & Thinking...")
    
    try:
        # 2. Download Voice
        voice_file_info = await bot.get_file(message.voice.file_id)
        voice_bytes = io.BytesIO()
        await bot.download_file(voice_file_info.file_path, destination=voice_bytes)
        
        # 3. Transcribe
        user_text = await transcribe_audio(voice_bytes)
        if not user_text:
            await processing_msg.edit_text("I couldn't hear you clearly. Please try again.")
            return

        # 4. AI Logic
        ai_output = await get_tutor_response(user_text)
        correction = ai_output.get("correction", "")
        reply_text = ai_output.get("response", "")

        # 5. TTS
        audio_reply = await text_to_speech(reply_text)
        
        # 6. Send Response
        await message.answer_voice(
            voice=BufferedInputFile(audio_reply.read(), filename="reply.ogg"),
            caption=f"🗣 **You said:** {user_text}\n\n✅ **Correction:** {correction}\n\n🤖 **Reply:** {reply_text}"
        )
        
        # 7. Update DB & Gamification
        await log_conversation(user_id, user_text, correction, reply_text)
        await add_xp(user_id, 10)
        
        await processing_msg.delete()
        
    except Exception as e:
        print(e)
        await processing_msg.edit_text("⚠️ Sorry, I had a brain freeze. Try again later.")

@dp.message(Command("upgrade"))
async def cmd_upgrade(message: types.Message):
    # MVP: Mock payment link
    await message.answer(
        "🚀 **Premium Plan: 49,000 UZS/month**\n\n"
        "Click below to pay via Payme (Mock):\n"
        "[Pay 49,000 UZS](https://payme.uz/fallback/mock)"
    )