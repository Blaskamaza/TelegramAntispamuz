import io
from openai import AsyncOpenAI
from src.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are 'InglizchaAI', a friendly English tutor for Uzbek students. 
1. Correct the user's grammar politely if there are mistakes.
2. Respond to their statement conversationally to keep the chat going.
3. Keep responses simple (CEFR A2-B1 level).
4. If the user speaks Uzbek, translate and guide them to English.
Output format: JSON { "correction": "...", "response": "..." }
"""

async def transcribe_audio(audio_bytes: io.BytesIO) -> str:
    """Convert Voice to Text (Whisper)"""
    audio_bytes.name = "voice.ogg" # OpenAI requires a filename
    transcript = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_bytes,
        language="en"
    )
    return transcript.text

async def get_tutor_response(user_text: str) -> dict:
    """Get logic/correction from GPT-4o-mini"""
    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        response_format={ "type": "json_object" }
    )
    import json
    return json.loads(completion.choices[0].message.content)

async def text_to_speech(text: str) -> io.BytesIO:
    """Convert text back to audio"""
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    # Stream to memory buffer
    audio_buffer = io.BytesIO()
    for chunk in response.iter_bytes():
        audio_buffer.write(chunk)
    audio_buffer.seek(0)
    return audio_buffer