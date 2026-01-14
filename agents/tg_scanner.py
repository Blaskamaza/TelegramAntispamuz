"""
Telegram Scanner Agent — Парсинг публичных каналов
Использует Telethon для доступа к Telegram API

ВАЖНО: При первом запуске потребуется авторизация через телефон!
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from config import (
    TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME,
    TELEGRAM_CHANNELS, PAIN_KEYWORDS, BLACKLIST_KEYWORDS, 
    FRESH_DIR, TODAY
)

# Telethon
try:
    from telethon import TelegramClient
    from telethon.tl.functions.messages import GetHistoryRequest
    from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    print("⚠️ Telethon not installed. Run: pip install telethon")


# ============================================================
# TELEGRAM CLIENT
# ============================================================

class TelegramScanner:
    """
    Сканер публичных Telegram каналов.
    Использует Telethon для парсинга постов.
    """
    
    def __init__(self, api_id: int, api_hash: str, session_name: str = "scanner"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client: Optional[TelegramClient] = None
    
    async def connect(self):
        """Подключается к Telegram"""
        if not TELETHON_AVAILABLE:
            print("❌ Telethon not available")
            return False
        
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        
        print("📱 Connecting to Telegram...")
        await self.client.start()
        
        me = await self.client.get_me()
        print(f"✅ Logged in as: {me.first_name} (@{me.username})")
        return True
    
    async def disconnect(self):
        """Отключается от Telegram"""
        if self.client:
            await self.client.disconnect()
            print("👋 Disconnected from Telegram")
    
    async def get_channel_posts(
        self, 
        channel_username: str, 
        limit: int = 50,
        days_back: int = 7
    ) -> List[Dict]:
        """
        Получает посты из канала за последние N дней.
        
        Args:
            channel_username: Username канала (с @ или без)
            limit: Максимум постов
            days_back: За сколько дней собирать
        
        Returns:
            Список постов с текстом и метаданными
        """
        if not self.client:
            return []
        
        channel_username = channel_username.lstrip("@")
        posts = []
        min_date = datetime.now() - timedelta(days=days_back)
        
        try:
            entity = await self.client.get_entity(channel_username)
            print(f"📡 Scanning: @{channel_username}")
            
            async for message in self.client.iter_messages(entity, limit=limit):
                if message.date.replace(tzinfo=None) < min_date:
                    break
                
                if message.text:
                    posts.append({
                        "id": message.id,
                        "text": message.text,
                        "date": message.date.isoformat(),
                        "views": message.views or 0,
                        "forwards": message.forwards or 0,
                        "channel": channel_username,
                    })
            
            print(f"   ✅ Found {len(posts)} posts")
            return posts
            
        except ChannelPrivateError:
            print(f"   ⚠️ Channel @{channel_username} is private")
            return []
        except UsernameNotOccupiedError:
            print(f"   ⚠️ Channel @{channel_username} not found")
            return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    async def scan_all_channels(
        self, 
        channels: List[str], 
        posts_per_channel: int = 30
    ) -> Dict:
        """Сканирует все каналы"""
        all_data = {
            "date": TODAY,
            "api_mode": True,
            "channels_scanned": 0,
            "total_posts": 0,
            "total_pains": 0,
            "channels": [],
        }
        
        for channel in channels:
            posts = await self.get_channel_posts(channel, limit=posts_per_channel)
            
            if posts:
                pains = extract_pains_from_posts(posts)
                
                channel_data = {
                    "channel": channel,
                    "posts_count": len(posts),
                    "pains_count": len(pains),
                    "pains": pains[:20],  # Топ 20 болей
                }
                
                all_data["channels"].append(channel_data)
                all_data["channels_scanned"] += 1
                all_data["total_posts"] += len(posts)
                all_data["total_pains"] += len(pains)
            
            # Пауза между каналами (anti-flood)
            await asyncio.sleep(1)
        
        return all_data


# ============================================================
# PAIN EXTRACTION
# ============================================================

def classify_post(text: str) -> Dict:
    """Классифицирует пост на боль/вопрос/нейтральный"""
    text_lower = text.lower()
    
    # Проверка blacklist
    for word in BLACKLIST_KEYWORDS:
        if word in text_lower:
            return {"type": "blocked", "reason": "blacklist"}
    
    # Классификация боли
    pain_score = 0
    matched_keywords = []
    
    for keyword in PAIN_KEYWORDS:
        if keyword in text_lower:
            pain_score += 1
            matched_keywords.append(keyword)
    
    if pain_score >= 2:
        return {"type": "pain", "score": pain_score, "keywords": matched_keywords}
    elif pain_score == 1:
        return {"type": "question", "score": pain_score, "keywords": matched_keywords}
    else:
        return {"type": "neutral", "score": 0, "keywords": []}


def extract_pains_from_posts(posts: List[Dict]) -> List[Dict]:
    """Извлекает боли из постов"""
    pains = []
    
    for post in posts:
        classification = classify_post(post["text"])
        
        if classification["type"] in ["pain", "question"]:
            pains.append({
                "text": post["text"][:500],  # Ограничение длины
                "type": classification["type"],
                "score": classification["score"],
                "keywords": classification["keywords"],
                "views": post.get("views", 0),
                "channel": post.get("channel", ""),
                "date": post.get("date", ""),
            })
    
    # Сортировка по score и views
    pains.sort(key=lambda x: (x["score"], x["views"]), reverse=True)
    return pains


# ============================================================
# MOCK DATA (когда Telethon недоступен)
# ============================================================

def get_mock_data() -> Dict:
    """Mock данные для тестирования без API"""
    import random
    
    mock_posts = [
        "Подскажите где найти хорошего репетитора по математике в Ташкенте?",
        "Ищу работу SMM-менеджера, опыт 2 года, помогите найти!",
        "Проблема с оплатой через Click, деньги списались но не прошло",
        "Kerak menga yordam, qanday qilib ro'yxatdan o'tish mumkin?",
        "Где купить iPhone дешевле всего в Ташкенте?",
        "Не работает приложение Payme, что делать?",
        "Ищу квартиру в аренду, до 3 млн сум, Чиланзар",
        "Подскажите хорошие IT курсы для начинающих",
        "Как оформить кредит без отказа? Нужно срочно",
        "Qayerda ingliz tilini o'rganish mumkin?",
    ]
    
    channels_data = []
    total_pains = 0
    
    for channel in TELEGRAM_CHANNELS[:6]:
        posts = []
        for i in range(random.randint(3, 8)):
            post_text = random.choice(mock_posts)
            posts.append({
                "id": i,
                "text": post_text,
                "date": datetime.now().isoformat(),
                "views": random.randint(100, 5000),
                "channel": channel,
            })
        
        pains = extract_pains_from_posts(posts)
        
        channels_data.append({
            "channel": channel,
            "posts_count": len(posts),
            "pains_count": len(pains),
            "pains": pains,
        })
        total_pains += len(pains)
    
    return {
        "date": TODAY,
        "api_mode": False,
        "channels_scanned": len(channels_data),
        "total_posts": sum(c["posts_count"] for c in channels_data),
        "total_pains": total_pains,
        "channels": channels_data,
    }


# ============================================================
# SAVE DATA
# ============================================================

def save_telegram_data(data: Dict) -> Path:
    """Сохраняет данные Telegram"""
    output_dir = FRESH_DIR / "telegram"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"uz_{TODAY}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved Telegram data to {output_file}")
    return output_file


# ============================================================
# MAIN
# ============================================================

async def run_async(use_api: bool = True):
    """Асинхронная версия запуска"""
    print("📱 Telegram Scanner Agent starting...")
    print(f"📅 Date: {TODAY}")
    print(f"🔑 API ID: {TELEGRAM_API_ID}")
    print(f"📡 Channels: {len(TELEGRAM_CHANNELS)}")
    
    if use_api and TELETHON_AVAILABLE:
        scanner = TelegramScanner(
            api_id=TELEGRAM_API_ID,
            api_hash=TELEGRAM_API_HASH,
            session_name=TELEGRAM_SESSION_NAME
        )
        
        try:
            connected = await scanner.connect()
            
            if connected:
                data = await scanner.scan_all_channels(TELEGRAM_CHANNELS)
            else:
                print("⚠️ Connection failed, using mock data")
                data = get_mock_data()
                
        finally:
            await scanner.disconnect()
    else:
        print("⚠️ Telethon not available, using mock data")
        data = get_mock_data()
    
    print(f"\n{'='*50}")
    print(f"📊 Results:")
    print(f"   Channels scanned: {data['channels_scanned']}")
    print(f"   Total posts: {data['total_posts']}")
    print(f"   Pains found: {data['total_pains']}")
    print(f"{'='*50}")
    
    save_telegram_data(data)
    return data


def run(use_api: bool = True):
    """Синхронная обёртка для запуска агента"""
    return asyncio.run(run_async(use_api))


if __name__ == "__main__":
    run(use_api=True)
