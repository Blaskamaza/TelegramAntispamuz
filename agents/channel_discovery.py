"""
Auto-Discovery Agent — Автоматический поиск новых Telegram каналов
Использует Perplexity API для поиска + Telethon для проверки

Функции:
1. Поиск новых каналов через Perplexity
2. Проверка существования канала через Telegram API
3. Автоматическое обновление telegram_channels.py
"""

import json
import re
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set

from config import (
    PERPLEXITY_API_KEY, PERPLEXITY_MODEL,
    TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME,
    FRESH_DIR, TODAY
)

# Импорт существующих каналов
try:
    from telegram_channels import TELEGRAM_CHANNELS, BROKEN_CHANNELS
except ImportError:
    TELEGRAM_CHANNELS = []
    BROKEN_CHANNELS = []


# ============================================================
# PERPLEXITY API
# ============================================================

class PerplexityClient:
    """
    Клиент для Perplexity API с профессиональными промптами.
    
    Возможности:
    - Поиск Telegram каналов
    - Поиск трендов и болей
    - Анализ рынка
    """
    
    API_URL = "https://api.perplexity.ai/chat/completions"
    
    # Профессиональные системные промпты
    PROMPTS = {
        "channels": """You are an expert Telegram channel researcher specializing in Uzbekistan.

Your task: Find REAL, ACTIVE Telegram channels that exist RIGHT NOW.

STRICT REQUIREMENTS:
1. Only return channels that are VERIFIED to exist (you searched for them)
2. Channels must have posts from the last 7 days
3. Prefer official channels with blue checkmarks
4. Include both Russian and Uzbek language channels
5. Return ONLY usernames in format: @username

DO NOT:
- Invent channel names
- Return inactive/dead channels
- Return private channels
- Add explanations

OUTPUT FORMAT:
@channel1
@channel2
@channel3""",

        "trends": """You are a market research expert analyzing trends in Uzbekistan.

TASK: Search for CURRENT, REAL-TIME trending topics, problems, and business opportunities in Uzbekistan.

RESEARCH SOURCES (search all):
1. Kun.uz, Daryo.uz, Gazeta.uz - news portals
2. TGStat Uzbekistan - Telegram analytics
3. Google Trends Uzbekistan
4. Social media discussions

WHAT TO FIND:
- Trending search queries this week
- Viral news topics
- Common problems people discuss (боли)
- Business opportunities
- Popular products/services
- Job market trends

OUTPUT FORMAT (JSON):
{
  "date": "YYYY-MM-DD",
  "hot_topics": ["topic1", "topic2"],
  "problems_pains": ["pain1", "pain2"],
  "business_opportunities": ["opportunity1"],
  "trending_products": ["product1"],
  "job_trends": ["trend1"]
}""",

        "pains": """You are a customer research specialist finding REAL PROBLEMS (боли) that people in Uzbekistan face.

TASK: Search for actual complaints, questions, and problems people discuss online.

SEARCH IN:
- Telegram groups and channels (comments)
- VK and Facebook groups
- Forums and Q&A sites
- News article comments
- Review sites

CATEGORIES TO RESEARCH:
- Работа/вакансии (job problems)
- Образование (education issues)
- Финансы/кредиты (money problems)
- Здоровье (health concerns)
- Жильё (housing issues)
- IT/технологии (tech problems)

OUTPUT FORMAT (JSON list):
[
  {"pain": "описание боли", "category": "категория", "frequency": "high/medium/low", "source": "откуда узнали"},
  ...
]

Return 15-20 real problems you found.""",
    }
    
    def __init__(self, api_key: str, model: str = "sonar"):
        self.api_key = api_key
        self.model = model
    
    def _request(self, system_prompt: str, user_query: str, temperature: float = 0.3) -> Optional[str]:
        """Выполняет запрос к Perplexity API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            "temperature": temperature,
            "max_tokens": 4000,
        }
        
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.API_URL, data=data, headers=headers)
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
                
        except urllib.error.HTTPError as e:
            print(f"⚠️ Perplexity API Error: {e.code}")
            try:
                error_body = e.read().decode("utf-8")
                print(f"   Details: {error_body[:200]}")
            except:
                pass
            return None
        except Exception as e:
            print(f"⚠️ Request failed: {e}")
            return None
    
    def find_telegram_channels(self, category: str, country: str = "Uzbekistan") -> List[str]:
        """
        Находит актуальные Telegram каналы.
        """
        query = f"""Search for active Telegram channels in {country} about: {category}

Current date: {datetime.now().strftime('%Y-%m-%d')}

Find channels that:
- Posted content in the last 7 days
- Have 1000+ subscribers
- Are public and accessible
- Cover: {category}

Search on: TGStat.ru, UzTelegram.com, Telegram search"""
        
        print(f"🔍 Perplexity: Searching '{category}' channels...")
        response = self._request(self.PROMPTS["channels"], query)
        
        if not response:
            return []
        
        # Извлекаем @username из ответа
        channels = re.findall(r'@[\w\d_]+', response)
        unique_channels = list(set(channels))
        
        print(f"   ✅ Found {len(unique_channels)} channels")
        return unique_channels
    
    def search_trends(self, country: str = "Uzbekistan") -> Dict:
        """
        Ищет актуальные тренды и горячие темы.
        
        Returns:
            Dict с трендами, болями, возможностями
        """
        query = f"""Search for what's trending in {country} RIGHT NOW.

Current date: {datetime.now().strftime('%Y-%m-%d')}

I need REAL, CURRENT data from:
1. Today's news from Kun.uz, Daryo.uz, Gazeta.uz
2. Trending topics on Telegram in Uzbekistan
3. Popular search queries
4. Viral social media discussions

Return ONLY verified, real information you found online."""
        
        print(f"🔥 Perplexity: Searching trends in {country}...")
        response = self._request(self.PROMPTS["trends"], query, temperature=0.2)
        
        if not response:
            return {}
        
        # Пытаемся распарсить JSON
        try:
            # Ищем JSON в ответе
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback: возвращаем как текст
        return {"raw_response": response}
    
    def find_pains(self, country: str = "Uzbekistan") -> List[Dict]:
        """
        Ищет реальные боли и проблемы людей.
        
        Returns:
            Список найденных болей
        """
        query = f"""Research real problems and complaints people in {country} have.

Current date: {datetime.now().strftime('%Y-%m-%d')}

Search in:
- Comments under news articles
- Telegram group discussions  
- VK and Facebook groups
- Forum posts and Q&A
- Review sites

Find problems about: работа, образование, финансы, жильё, здоровье, IT"""
        
        print(f"💊 Perplexity: Searching pains in {country}...")
        response = self._request(self.PROMPTS["pains"], query, temperature=0.3)
        
        if not response:
            return []
        
        # Пытаемся распарсить JSON список
        try:
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback
        return [{"raw_response": response}]


# ============================================================
# TELEGRAM CHANNEL VERIFIER
# ============================================================

async def verify_channels_exist(channels: List[str]) -> Dict[str, bool]:
    """
    Проверяет существование каналов через Telegram API.
    
    Returns:
        Dict с результатами: {"@channel": True/False}
    """
    try:
        from telethon import TelegramClient
        from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
    except ImportError:
        print("⚠️ Telethon not installed")
        return {ch: None for ch in channels}
    
    results = {}
    client = TelegramClient(TELEGRAM_SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.start()
        print(f"📱 Verifying {len(channels)} channels...")
        
        for channel in channels:
            username = channel.lstrip("@")
            try:
                entity = await client.get_entity(username)
                results[channel] = True
                print(f"   ✅ {channel} exists")
            except (UsernameNotOccupiedError, UsernameInvalidError):
                results[channel] = False
                print(f"   ❌ {channel} not found")
            except Exception as e:
                results[channel] = False
                print(f"   ⚠️ {channel} error: {e}")
            
            # Пауза для избежания FloodWait
            import asyncio
            await asyncio.sleep(0.5)
    
    finally:
        await client.disconnect()
    
    return results


# ============================================================
# CHANNEL LIST UPDATER
# ============================================================

def update_channels_file(new_channels: List[str], broken_channels: List[str]):
    """
    Обновляет telegram_channels.py с новыми каналами.
    """
    channels_file = Path(__file__).parent / "telegram_channels.py"
    
    # Читаем текущий файл
    if channels_file.exists():
        content = channels_file.read_text(encoding="utf-8")
    else:
        content = ""
    
    # Находим все существующие каналы
    existing = set(re.findall(r'"@[\w\d_]+"', content))
    existing = {ch.strip('"') for ch in existing}
    
    # Добавляем новые (исключая broken)
    broken_set = set(broken_channels)
    added = []
    
    for channel in new_channels:
        if channel not in existing and channel not in broken_set:
            added.append(channel)
            existing.add(channel)
    
    if added:
        print(f"📝 Adding {len(added)} new channels to telegram_channels.py")
        
        # Добавляем в конец списка TELEGRAM_CHANNELS
        # Находим последний ] в TELEGRAM_CHANNELS
        insert_pos = content.rfind("]", content.find("TELEGRAM_CHANNELS"))
        
        if insert_pos > 0:
            new_entries = "\n".join([f'    "{ch}",  # AUTO-DISCOVERED {TODAY}' for ch in added])
            content = content[:insert_pos] + "\n    # === AUTO-DISCOVERED ===\n" + new_entries + "\n" + content[insert_pos:]
            
            channels_file.write_text(content, encoding="utf-8")
            print(f"   ✅ Saved: {added}")
    else:
        print("   ℹ️ No new channels to add")
    
    return added


# ============================================================
# DISCOVERY CATEGORIES
# ============================================================

DISCOVERY_CATEGORIES = [
    "работа вакансии jobs",
    "IT программирование developers coding",
    "образование университеты DTM",
    "бизнес стартапы entrepreneurship",
    "новости news Tashkent",
    "финансы банки кредиты",
    "недвижимость аренда квартиры",
    "автомобили машины авторынок",
    "фриланс удаленная работа",
    "курсы обучение онлайн",
]


# ============================================================
# MAIN
# ============================================================

def run_discovery(use_perplexity: bool = True, verify: bool = True):
    """
    Запускает процесс обнаружения новых каналов.
    
    Args:
        use_perplexity: Использовать Perplexity для поиска
        verify: Проверять каналы через Telegram
    """
    print("🔍 Auto-Discovery Agent starting...")
    print(f"📅 Date: {TODAY}")
    print(f"🔑 Perplexity API: {'✅' if PERPLEXITY_API_KEY else '❌'}")
    
    all_discovered = []
    
    if use_perplexity and PERPLEXITY_API_KEY:
        client = PerplexityClient(PERPLEXITY_API_KEY, PERPLEXITY_MODEL)
        
        for category in DISCOVERY_CATEGORIES:
            channels = client.find_telegram_channels(category)
            all_discovered.extend(channels)
            
            # Пауза между запросами
            import time
            time.sleep(2)
    
    # Убираем дубликаты
    all_discovered = list(set(all_discovered))
    
    # Убираем уже известные
    existing = set(TELEGRAM_CHANNELS)
    broken = set(BROKEN_CHANNELS)
    new_channels = [ch for ch in all_discovered if ch not in existing and ch not in broken]
    
    print(f"\n📊 Discovery Results:")
    print(f"   Total found: {len(all_discovered)}")
    print(f"   New channels: {len(new_channels)}")
    
    # Верификация через Telegram
    verified_channels = []
    if verify and new_channels:
        import asyncio
        results = asyncio.run(verify_channels_exist(new_channels[:30]))  # Лимит 30
        verified_channels = [ch for ch, exists in results.items() if exists]
        print(f"   Verified: {len(verified_channels)}")
    
    # Обновляем файл
    if verified_channels:
        added = update_channels_file(verified_channels, list(broken))
    else:
        added = []
    
    # Сохраняем лог
    log_data = {
        "date": TODAY,
        "categories_searched": len(DISCOVERY_CATEGORIES),
        "total_discovered": len(all_discovered),
        "new_channels": new_channels,
        "verified": verified_channels,
        "added": added,
    }
    
    log_dir = FRESH_DIR / "discovery"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"discovery_{TODAY}.json"
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Discovery log saved to {log_file}")
    return log_data


if __name__ == "__main__":
    run_discovery(use_perplexity=True, verify=True)
