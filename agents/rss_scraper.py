"""
RSS Scanner Agent — Парсинг RSS лент узбекских СМИ
Использует feedparser для получения новостей

БЕСПЛАТНО: Без лимитов
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from config import RSS_FEEDS, PAIN_KEYWORDS, BLACKLIST_KEYWORDS, FRESH_DIR, TODAY

# Feedparser
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("⚠️ feedparser not installed. Run: pip install feedparser")


class RSSScanner:
    """
    Сканер RSS лент для сбора новостей.
    """
    
    def __init__(self, feeds: List[str]):
        """
        Args:
            feeds: Список URL RSS лент
        """
        self.feeds = feeds
    
    def fetch_feed(self, url: str) -> List[Dict]:
        """
        Парсит одну RSS ленту.
        
        Returns:
            Список записей
        """
        if not FEEDPARSER_AVAILABLE:
            return []
        
        try:
            print(f"📰 Fetching: {url}")
            feed = feedparser.parse(url)
            
            if feed.bozo:  # Ошибка парсинга
                print(f"   ⚠️ Parse error: {feed.bozo_exception}")
            
            entries = []
            for entry in feed.entries[:30]:  # Макс 30 записей
                entries.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "published": entry.get("published", ""),
                    "source": feed.feed.get("title", url),
                })
            
            print(f"   ✅ Found {len(entries)} entries")
            return entries
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def fetch_all_feeds(self) -> List[Dict]:
        """
        Парсит все RSS ленты.
        
        Returns:
            Объединённый список записей
        """
        all_entries = []
        
        for url in self.feeds:
            entries = self.fetch_feed(url)
            all_entries.extend(entries)
        
        return all_entries


def classify_entry(text: str) -> Dict:
    """Классифицирует запись"""
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


def extract_pains_from_entries(entries: List[Dict]) -> List[Dict]:
    """
    Извлекает боли из записей RSS.
    """
    pains = []
    
    for entry in entries:
        # Объединяем title и summary для анализа
        full_text = f"{entry.get('title', '')} {entry.get('summary', '')}"
        classification = classify_entry(full_text)
        
        if classification["type"] in ["pain", "question"]:
            pains.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "source": entry.get("source", ""),
                "type": classification["type"],
                "score": classification["score"],
                "keywords": classification["keywords"],
            })
    
    return sorted(pains, key=lambda x: x["score"], reverse=True)


def save_rss_data(data: Dict) -> Path:
    """Сохраняет данные RSS"""
    output_dir = FRESH_DIR / "rss"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"uz_{TODAY}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved RSS data to {output_file}")
    return output_file


def run():
    """Основная функция агента"""
    print("📰 RSS Scanner Agent starting...")
    print(f"📅 Date: {TODAY}")
    print(f"📡 Feeds: {len(RSS_FEEDS)}")
    print(f"🔑 Feedparser: {'✅' if FEEDPARSER_AVAILABLE else '❌ Not available'}")
    
    scanner = RSSScanner(RSS_FEEDS)
    
    # 1. Получаем все записи
    print("\n🔍 Fetching RSS feeds...")
    entries = scanner.fetch_all_feeds()
    
    # 2. Извлекаем боли
    print("\n💊 Extracting pains...")
    pains = extract_pains_from_entries(entries)
    print(f"   Found {len(pains)} pains")
    
    # 3. Группировка по источникам
    sources = {}
    for entry in entries:
        source = entry.get("source", "Unknown")
        if source not in sources:
            sources[source] = 0
        sources[source] += 1
    
    # Результаты
    all_data = {
        "date": TODAY,
        "feeds_count": len(RSS_FEEDS),
        "entries_count": len(entries),
        "pains_count": len(pains),
        "sources": sources,
        "entries": entries[:50],  # Топ 50 записей
        "pains": pains[:30],  # Топ 30 болей
    }
    
    print(f"\n{'='*50}")
    print(f"📊 Results:")
    print(f"   Feeds parsed: {len(RSS_FEEDS)}")
    print(f"   Total entries: {len(entries)}")
    print(f"   Pains found: {len(pains)}")
    print(f"{'='*50}")
    
    save_rss_data(all_data)
    return all_data


if __name__ == "__main__":
    run()
