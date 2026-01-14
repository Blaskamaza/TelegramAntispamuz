"""
VK Scanner Agent — Парсинг публичных групп VK
Использует VK API для получения постов

API Ключ: Бесплатный, нужен сервисный ключ
Лимит: 5 req/sec

КАК ПОЛУЧИТЬ КЛЮЧ:
1. Зайди на https://vk.com/apps?act=manage
2. Создай новое приложение (Standalone)
3. Получи "Сервисный ключ доступа" в настройках
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from config import PAIN_KEYWORDS, BLACKLIST_KEYWORDS, FRESH_DIR, TODAY

# Попытка импорта API ключа из config
try:
    from config import VK_SERVICE_KEY
except ImportError:
    VK_SERVICE_KEY = ""


# Список узбекистанских VK групп
VK_GROUPS = [
    "rabota_tashkent",       # Работа в Ташкенте
    "it_uzbekistan",         # IT Uzbekistan
    "tashkent_city",         # Ташкент
    "uzbekistan_news",       # Новости Узбекистана
    "business_uzbekistan",   # Бизнес Узбекистан
    "freelance_uz",          # Фриланс УЗ
    "study_abroad_uz",       # Учёба за рубежом
    "kuply_prodam_tashkent", # Купля-продажа
]


class VKScanner:
    """
    Сканер публичных групп VK.
    """
    
    API_URL = "https://api.vk.com/method"
    API_VERSION = "5.199"
    
    def __init__(self, access_token: str):
        """
        Args:
            access_token: Сервисный ключ доступа VK
        """
        self.access_token = access_token
    
    def _request(self, method: str, params: dict) -> Optional[dict]:
        """Выполняет запрос к VK API"""
        params["access_token"] = self.access_token
        params["v"] = self.API_VERSION
        
        url = f"{self.API_URL}/{method}?{urllib.parse.urlencode(params)}"
        
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                if "error" in result:
                    error = result["error"]
                    print(f"   ⚠️ VK Error: {error.get('error_msg', 'Unknown')}")
                    return None
                
                return result.get("response")
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
            return None
    
    def get_wall_posts(self, group_id: str, count: int = 30) -> List[Dict]:
        """
        Получает посты со стены группы.
        
        Args:
            group_id: ID или short_name группы (без минуса)
            count: Количество постов
        
        Returns:
            Список постов
        """
        print(f"📡 Fetching VK: {group_id}")
        
        response = self._request("wall.get", {
            "domain": group_id,
            "count": min(count, 100),
            "filter": "all",
        })
        
        if not response:
            return []
        
        posts = []
        for item in response.get("items", []):
            posts.append({
                "id": item.get("id"),
                "text": item.get("text", "")[:500],
                "date": datetime.fromtimestamp(item.get("date", 0)).isoformat(),
                "likes": item.get("likes", {}).get("count", 0),
                "comments": item.get("comments", {}).get("count", 0),
                "views": item.get("views", {}).get("count", 0),
                "group": group_id,
            })
        
        print(f"   ✅ Found {len(posts)} posts")
        return posts
    
    def search_posts(self, query: str, count: int = 50) -> List[Dict]:
        """
        Поиск постов по запросу.
        
        Args:
            query: Поисковый запрос
            count: Количество результатов
        
        Returns:
            Список постов
        """
        print(f"🔍 VK Search: '{query}'")
        
        response = self._request("newsfeed.search", {
            "q": query,
            "count": min(count, 200),
            "extended": 0,
        })
        
        if not response:
            return []
        
        posts = []
        for item in response.get("items", []):
            posts.append({
                "id": item.get("id"),
                "text": item.get("text", "")[:500],
                "date": datetime.fromtimestamp(item.get("date", 0)).isoformat(),
                "likes": item.get("likes", {}).get("count", 0),
                "owner_id": item.get("owner_id"),
            })
        
        print(f"   ✅ Found {len(posts)} posts")
        return posts


def classify_post(text: str) -> Dict:
    """Классифицирует пост"""
    text_lower = text.lower()
    
    # Проверка blacklist
    for word in BLACKLIST_KEYWORDS:
        if word in text_lower:
            return {"type": "blocked", "score": 0, "keywords": []}
    
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
    """Извлекает боли из постов VK"""
    pains = []
    
    for post in posts:
        classification = classify_post(post.get("text", ""))
        
        if classification["type"] in ["pain", "question"]:
            pains.append({
                "text": post.get("text", "")[:300],
                "group": post.get("group", ""),
                "type": classification["type"],
                "score": classification["score"],
                "keywords": classification["keywords"],
                "likes": post.get("likes", 0),
                "views": post.get("views", 0),
            })
    
    return sorted(pains, key=lambda x: x["score"], reverse=True)


def get_mock_data() -> Dict:
    """Mock данные когда нет API ключа"""
    import random
    
    mock_posts = [
        "Ищу работу программистом в Ташкенте, опыт 2 года Python",
        "Подскажите хорошие курсы английского языка",
        "Где купить iPhone дешевле всего?",
        "Проблема с оплатой через Click, помогите!",
        "Ищу репетитора по математике для подготовки к DTM",
        "Сдаю квартиру в центре Ташкента, 3 комнаты",
        "Как оформить визу в Корею?",
        "Нужен хороший стоматолог, посоветуйте",
    ]
    
    posts = []
    for i, text in enumerate(mock_posts):
        posts.append({
            "id": i,
            "text": text,
            "date": datetime.now().isoformat(),
            "likes": random.randint(0, 50),
            "views": random.randint(100, 1000),
            "group": "mock_group",
        })
    
    pains = extract_pains_from_posts(posts)
    
    return {
        "date": TODAY,
        "api_mode": False,
        "groups_count": 0,
        "posts_count": len(posts),
        "pains_count": len(pains),
        "posts": posts,
        "pains": pains,
    }


def save_vk_data(data: Dict) -> Path:
    """Сохраняет данные VK"""
    output_dir = FRESH_DIR / "vk"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"uz_{TODAY}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved VK data to {output_file}")
    return output_file


def run(use_api: bool = True):
    """Основная функция агента"""
    print("💬 VK Scanner Agent starting...")
    print(f"📅 Date: {TODAY}")
    print(f"🔑 VK API Key: {'✅ Configured' if VK_SERVICE_KEY else '❌ Not configured'}")
    
    if not VK_SERVICE_KEY or not use_api:
        print("⚠️ Using mock data (no API key)")
        data = get_mock_data()
        save_vk_data(data)
        return data
    
    scanner = VKScanner(VK_SERVICE_KEY)
    
    all_posts = []
    
    # Получаем посты из групп
    print("\n🔍 Fetching posts from groups...")
    for group in VK_GROUPS[:5]:  # Лимит 5 групп
        posts = scanner.get_wall_posts(group)
        all_posts.extend(posts)
        
        # Пауза между запросами (5 req/sec)
        import time
        time.sleep(0.3)
    
    # Извлекаем боли
    print("\n💊 Extracting pains...")
    pains = extract_pains_from_posts(all_posts)
    print(f"   Found {len(pains)} pains")
    
    # Результаты
    all_data = {
        "date": TODAY,
        "api_mode": True,
        "groups_count": len(VK_GROUPS),
        "posts_count": len(all_posts),
        "pains_count": len(pains),
        "posts": all_posts[:50],
        "pains": pains[:30],
    }
    
    print(f"\n{'='*50}")
    print(f"📊 Results:")
    print(f"   Groups: {len(VK_GROUPS)}")
    print(f"   Posts: {len(all_posts)}")
    print(f"   Pains: {len(pains)}")
    print(f"{'='*50}")
    
    save_vk_data(all_data)
    return all_data


if __name__ == "__main__":
    run(use_api=True)
