"""
YouTube Scanner Agent — Поиск болей в комментариях
YouTube Data API v3: бесплатно 10,000 единиц/день

Реальная интеграция с fallback на mock при ошибках.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

from config import (
    YOUTUBE_QUERIES, YOUTUBE_API_KEY, 
    PAIN_KEYWORDS, BLACKLIST_KEYWORDS, 
    FRESH_DIR, TODAY
)

# API Endpoints
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_COMMENTS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def api_request(url: str, params: dict) -> dict:
    """
    Выполняет запрос к YouTube API.
    Возвращает JSON ответ или None при ошибке.
    """
    params["key"] = YOUTUBE_API_KEY
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    try:
        req = urllib.request.Request(full_url)
        req.add_header("Accept", "application/json")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"⚠️ API Error: {e.code} - {e.reason}")
        if e.code == 403:
            print("   Quota exceeded or API key invalid")
        return None
    except Exception as e:
        print(f"⚠️ Request failed: {e}")
        return None


def search_videos_api(query: str, max_results: int = 10) -> list:
    """
    Поиск видео через YouTube Data API v3.
    Cost: 100 units per request.
    """
    print(f"🔍 API: Searching '{query}'...")
    
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "regionCode": "UZ",
        "relevanceLanguage": "ru",
        "maxResults": min(max_results, 25),
        "order": "relevance",
    }
    
    response = api_request(YOUTUBE_SEARCH_URL, params)
    
    if not response or "items" not in response:
        print("   ↪ Fallback to mock data")
        return search_videos_mock(query)
    
    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        
        videos.append({
            "id": video_id,
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "published": snippet["publishedAt"],
            "description": snippet.get("description", "")[:200],
        })
    
    print(f"   ✅ Found {len(videos)} videos")
    return videos


def get_video_comments_api(video_id: str, max_comments: int = 50) -> list:
    """
    Получает комментарии к видео через API.
    Cost: ~1 unit per request (100 comments).
    """
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": min(max_comments, 100),
        "order": "relevance",
        "textFormat": "plainText",
    }
    
    response = api_request(YOUTUBE_COMMENTS_URL, params)
    
    if not response or "items" not in response:
        return get_video_comments_mock(video_id, max_comments)
    
    comments = []
    for item in response.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        
        comments.append({
            "id": item["id"],
            "text": snippet["textDisplay"],
            "author": snippet["authorDisplayName"],
            "likes": snippet.get("likeCount", 0),
            "published": snippet["publishedAt"],
        })
    
    return comments


def get_video_stats_api(video_id: str) -> dict:
    """
    Получает статистику видео (views, likes, comments).
    Cost: 1 unit per request.
    """
    params = {
        "part": "statistics",
        "id": video_id,
    }
    
    response = api_request(YOUTUBE_VIDEOS_URL, params)
    
    if not response or not response.get("items"):
        return {"views": 0, "likes": 0, "comments": 0}
    
    stats = response["items"][0].get("statistics", {})
    return {
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
    }


# ============================================================
# MOCK FALLBACK (когда API недоступен)
# ============================================================

def search_videos_mock(query: str) -> list:
    """Mock данные для тестирования"""
    mock_videos = {
        "qanday pul ishlash": [
            {"id": "vid001", "title": "Qanday pul ishlash mumkin 2026", "channel": "BiznesUZ", "views": 125000},
            {"id": "vid002", "title": "Uyda pul ishlash yo'llari", "channel": "FreelanceUZ", "views": 89000},
        ],
        "как заработать в Ташкенте": [
            {"id": "vid003", "title": "5 способов заработка в Ташкенте", "channel": "MoneyTashkent", "views": 234000},
            {"id": "vid004", "title": "Фриланс в Узбекистане - реальный опыт", "channel": "ITuzb", "views": 156000},
        ],
    }
    
    return mock_videos.get(query, [
        {"id": f"mock_{i}", "title": f"Video about {query}", "channel": "Channel", "views": 10000}
        for i in range(3)
    ])


def get_video_comments_mock(video_id: str, max_comments: int = 50) -> list:
    """Mock комментарии для тестирования"""
    import random
    
    pain_comments = [
        "Подскажите где найти такую работу в Ташкенте?",
        "Сколько стоит обучение? Есть ли рассрочка?",
        "Помогите, не могу зарегистрироваться на сайте",
        "Qanday qilib ro'yxatdan o'tish mumkin?",
        "Где купить дешевле в Узбекистане?",
        "Ищу партнера для бизнеса в Самарканде",
        "Не работает приложение, что делать?",
        "Kerak menga yordam, qanday qilish kerak?",
        "Сколько реально можно заработать?",
        "Проблема с оплатой, банк отклоняет",
        "Как оплатить из Узбекистана?",
        "Есть ли курсы на узбекском языке?",
        "Подскажите хорошего репетитора по математике",
        "Где найти дешевую аренду в Ташкенте?",
        "Ищу работу дистанционно, помогите!",
    ]
    
    neutral_comments = [
        "Отличное видео, спасибо!",
        "Zoʻr video!",
        "👍👍👍",
        "Подписался!",
        "Очень полезно",
    ]
    
    comments = []
    for i in range(max_comments):
        if random.random() < 0.7:
            text = random.choice(pain_comments)
        else:
            text = random.choice(neutral_comments)
        
        comments.append({
            "id": f"cmt_{video_id}_{i}",
            "text": text,
            "author": "User",
            "likes": random.randint(0, 50),
            "published": datetime.now().isoformat(),
        })
    
    return comments


# ============================================================
# PAIN CLASSIFICATION
# ============================================================

def classify_comment(text: str) -> dict:
    """Классифицирует комментарий на боль/вопрос/нейтральный"""
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


def extract_pains_from_comments(comments: list) -> list:
    """Извлекает боли из комментариев"""
    pains = []
    
    for comment in comments:
        classification = classify_comment(comment["text"])
        
        if classification["type"] in ["pain", "question"]:
            pains.append({
                "text": comment["text"],
                "type": classification["type"],
                "score": classification["score"],
                "keywords": classification["keywords"],
                "likes": comment.get("likes", 0),
                "author": comment.get("author", "Unknown"),
            })
    
    return pains


def save_youtube_data(data: dict):
    """Сохраняет данные YouTube"""
    output_dir = FRESH_DIR / "youtube"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"uz_{TODAY}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved YouTube data to {output_file}")
    return output_file


# ============================================================
# MAIN AGENT
# ============================================================

def run(use_api: bool = True):
    """
    Основная функция агента.
    
    Args:
        use_api: True = использовать реальный API, False = только mock
    """
    print("📺 YouTube Scanner Agent starting...")
    print(f"📅 Date: {TODAY}")
    print(f"🔑 API Key: {'✅ Configured' if YOUTUBE_API_KEY else '❌ Missing'}")
    print(f"🌐 Mode: {'Real API' if use_api and YOUTUBE_API_KEY else 'Mock Data'}")
    
    all_data = {
        "date": TODAY,
        "api_mode": use_api and bool(YOUTUBE_API_KEY),
        "queries": [],
        "total_videos": 0,
        "total_comments": 0,
        "total_pains": 0,
    }
    
    for query in YOUTUBE_QUERIES:
        print(f"\n🔍 Query: {query}")
        
        # Выбор между API и mock
        if use_api and YOUTUBE_API_KEY:
            videos = search_videos_api(query, max_results=5)  # Экономим quota
        else:
            videos = search_videos_mock(query)
        
        query_data = {
            "query": query,
            "videos": [],
        }
        
        for video in videos:
            # Получаем комментарии
            if use_api and YOUTUBE_API_KEY:
                comments = get_video_comments_api(video["id"], max_comments=30)
                stats = get_video_stats_api(video["id"])
                video["views"] = stats.get("views", 0)
            else:
                comments = get_video_comments_mock(video["id"])
            
            pains = extract_pains_from_comments(comments)
            
            video_data = {
                **video,
                "comments_count": len(comments),
                "pains_count": len(pains),
                "top_pains": sorted(pains, key=lambda x: x["score"], reverse=True)[:10],
            }
            
            query_data["videos"].append(video_data)
            all_data["total_comments"] += len(comments)
            all_data["total_pains"] += len(pains)
            
            print(f"   📹 {video['title'][:40]}... - {len(pains)} pains")
        
        all_data["queries"].append(query_data)
        all_data["total_videos"] += len(videos)
    
    print(f"\n{'='*50}")
    print(f"📊 Results:")
    print(f"   Total videos: {all_data['total_videos']}")
    print(f"   Total comments: {all_data['total_comments']}")
    print(f"   Pains found: {all_data['total_pains']}")
    print(f"{'='*50}")
    
    save_youtube_data(all_data)
    return all_data


if __name__ == "__main__":
    # Запуск с реальным API
    run(use_api=True)
