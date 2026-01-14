"""
Pain Extractor Agent — Анализ болей с помощью Gemini
Использует Gemini 3.0 Flash для классификации и Gemini 3.0 Pro для глубокого анализа.
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
from collections import Counter
from typing import List, Dict

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from config import (
    FRESH_DIR, TODAY, BASE_DIR, GOOGLE_API_KEY,
    GEMINI_PRO_MODEL, GEMINI_FLASH_MODEL, GEMINI_LITE_MODEL,
    GEMINI_RPM, GEMINI_RPD
)

# Настройка Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("⚠️ GOOGLE_API_KEY not found in config/env. AI features will be disabled.")


class RateLimiter:
    """Класс для управления лимитами API"""
    def __init__(self, rpm: int, rpd: int):
        self.rpm = rpm
        self.rpd = rpd
        self.requests_today = 0
        self.last_request_time = 0
        self.min_interval = 60.0 / rpm

    def wait(self):
        """Ожидание перед запросом"""
        if self.requests_today >= self.rpd:
            raise Exception("Daily API limit reached!")
        
        now = time.time()
        elapsed = now - self.last_request_time
        
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_request_time = time.time()
        self.requests_today += 1


# Инициализация лимитера
limiter = RateLimiter(rpm=GEMINI_RPM, rpd=GEMINI_RPD)


def load_all_fresh_data() -> dict:
    """Загружает все свежие данные из data/fresh/"""
    all_data = {
        "trends": [],
        "youtube": [],
        "telegram": [],
        "facebook": [],
        "rss": [],
    }
    
    for source in all_data.keys():
        source_dir = FRESH_DIR / source
        if source_dir.exists():
            for file in source_dir.glob(f"*{TODAY}*.json"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        all_data[source].append(data)
                except Exception as e:
                    print(f"⚠️ Error loading {file}: {e}")
    
    return all_data


def extract_pain_texts(data: dict) -> list:
    """Извлекает все тексты с болями из данных"""
    pain_texts = []
    
    # Trends
    for trends_data in data.get("trends", []):
        for trend in trends_data.get("data", []):
            if trend.get("growth_3m", 0) > 20:
                pain_texts.append({
                    "text": trend.get("keyword", ""),
                    "source": "Google Trends",
                    "score": trend.get("growth_3m", 0),
                })
    
    # YouTube
    for yt_data in data.get("youtube", []):
        for query in yt_data.get("queries", []):
            for video in query.get("videos", []):
                for pain in video.get("top_pains", []):
                    pain_texts.append({
                        "text": pain.get("text", ""),
                        "source": "YouTube",
                        "score": pain.get("score", 0),
                    })
    
    # Telegram
    for tg_data in data.get("telegram", []):
        for channel in tg_data.get("channels", []):
            for post in channel.get("pains", []): # Changed from pain_posts to pains based on tg_scanner
                pain_texts.append({
                    "text": post.get("text", ""),
                    "source": f"Telegram: {channel.get('channel', '')}",
                    "score": post.get("score", 0),
                })
    
    # Facebook
    for fb_data in data.get("facebook", []):
        for group in fb_data.get("groups", []):
            for post in group.get("pain_posts", []):
                pain_texts.append({
                    "text": post.get("text", ""),
                    "source": f"Facebook: {group.get('name', '')}",
                    "score": post.get("pain_score", 0) + post.get("engagement_score", 0) / 10,
                })
    
    # RSS
    for rss_data in data.get("rss", []):
        for feed in rss_data.get("feeds", []):
            for article in feed.get("pain_articles", []):
                pain_texts.append({
                    "text": f"{article.get('title', '')} - {article.get('summary', '')}",
                    "source": "RSS News",
                    "score": article.get("relevance_score", 0),
                })
    
    return pain_texts


def call_gemini(model_name: str, prompt: str) -> str:
    """Вызов Gemini API с обработкой ошибок и лимитов"""
    if not GOOGLE_API_KEY:
        return ""
        
    try:
        limiter.wait()
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error ({model_name}): {e}")
        return ""


def analyze_pains_with_gemini(pain_texts: list) -> list:
    """
    Двухэтапный анализ болей:
    1. Gemini 3.0 Flash: Классификация и фильтрация (Batching)
    2. Gemini 3.0 Pro: Глубокий анализ категорий и генерация идей
    """
    if not pain_texts:
        return []
        
    print(f"   Processing {len(pain_texts)} items...")
    
    # === ЭТАП 1: КЛАССИФИКАЦИЯ (Flash) ===
    print("   🚀 Stage 1: Categorization (Gemini Flash)...")
    
    # Разбиваем на батчи по 20 штук
    batch_size = 20
    batches = [pain_texts[i:i + batch_size] for i in range(0, len(pain_texts), batch_size)]
    
    categories_data = {}
    
    for i, batch in enumerate(batches):
        print(f"      Processing batch {i+1}/{len(batches)}...")
        
        batch_text = "\n".join([f"- {p['text']} (Source: {p['source']})" for p in batch])
        
        prompt = f"""
        Ты аналитик данных. Твоя задача — классифицировать жалобы и проблемы пользователей из списка ниже.
        
        Список:
        {batch_text}
        
        Для каждой жалобы определи категорию из списка:
        [Работа, Образование, Финансы, Технологии, Семья, Жильё, Бизнес, Покупки, Здоровье, Другое]
        
        Игнорируй мусор, спам и нерелевантные сообщения.
        
        Верни ответ ТОЛЬКО в формате JSON:
        [
            {{"text": "текст жалобы", "category": "Категория", "is_relevant": true/false}}
        ]
        """
        
        response_text = call_gemini(GEMINI_FLASH_MODEL, prompt)
        
        try:
            # Очистка markdown блоков json
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            results = json.loads(cleaned_text)
            
            for res in results:
                if res.get("is_relevant"):
                    cat = res.get("category", "Другое")
                    if cat not in categories_data:
                        categories_data[cat] = []
                    categories_data[cat].append(res.get("text"))
                    
        except Exception as e:
            print(f"      ⚠️ Batch parsing error: {e}")
            
    # === ЭТАП 2: ГЛУБОКИЙ АНАЛИЗ (Pro) ===
    print(f"   🧠 Stage 2: Deep Analysis (Gemini Pro)...")
    print(f"      Found {len(categories_data)} categories.")
    
    top_pains = []
    
    for category, texts in categories_data.items():
        if len(texts) < 3: # Пропускаем слишком маленькие категории
            continue
            
        print(f"      Analyzing category: {category} ({len(texts)} items)...")
        
        # Берем топ-50 текстов для анализа, чтобы не перегружать контекст
        analysis_text = "\n".join(texts[:50])
        
        prompt = f"""
        Ты — опытный продуктовый менеджер и предприниматель.
        Проанализируй список проблем пользователей в категории "{category}".
        
        Данные:
        {analysis_text}
        
        Твоя задача:
        1. Выдели самую острую и массовую "боль" в этой категории.
        2. Оцени частоту (на основе количества жалоб).
        3. Предложи конкретную бизнес-идею (MVP) для решения этой боли в Узбекистане.
        4. Оцени потенциал монетизации (сколько люди готовы платить).
        
        Верни ответ ТОЛЬКО в формате JSON:
        {{
            "category": "{category}",
            "frequency": {len(texts)},
            "pain_summary": "Краткое описание главной боли",
            "potential": "Низкий/Средний/Высокий",
            "price_hint": "Примерная цена (сум)",
            "business_idea": "Описание идеи MVP",
            "examples": ["Пример 1", "Пример 2", "Пример 3"]
        }}
        """
        
        response_text = call_gemini(GEMINI_PRO_MODEL, prompt)
        
        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            analysis = json.loads(cleaned_text)
            # Добавляем источники (фейковые для агрегации, так как мы их потеряли на этапе 1 для экономии токенов, 
            # но в реальном проекте стоит прокидывать)
            analysis["sources"] = ["Aggregated"] 
            top_pains.append(analysis)
        except Exception as e:
             print(f"      ⚠️ Category analysis error: {e}")

    # Сортировка по частоте
    top_pains.sort(key=lambda x: x["frequency"], reverse=True)
    return top_pains


def save_top_pains(pains: list):
    """Сохраняет топ болей в Markdown"""
    output_file = BASE_DIR / "data" / f"top_pains_{TODAY}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# 🎯 Топ Болей Узбекистана — {TODAY}\n\n")
        f.write(f"> Сгенерировано AI: {GEMINI_FLASH_MODEL} (Filter) + {GEMINI_PRO_MODEL} (Analysis)\n\n")
        
        for i, pain in enumerate(pains, 1):
            f.write(f"## {i}. {pain['category']}\n\n")
            f.write(f"- **Суть проблемы:** {pain['pain_summary']}\n")
            f.write(f"- **Частота:** {pain['frequency']} жалоб\n")
            f.write(f"- **Потенциал:** {pain['potential']}\n")
            f.write(f"- **Цена решения:** {pain['price_hint']}\n\n")
            
            f.write(f"### 💡 Бизнес-идея\n")
            f.write(f"{pain['business_idea']}\n\n")
            
            f.write(f"### Примеры жалоб\n")
            for example in pain.get('examples', []):
                f.write(f"- \"{example}\"\n")
            f.write("\n---\n\n")
    
    print(f"✅ Saved top pains to {output_file}")
    return output_file


def run():
    """Основная функция агента"""
    print("🧠 Pain Extractor Agent starting...")
    print(f"📅 Date: {TODAY}")
    print(f"🤖 Models: {GEMINI_FLASH_MODEL} + {GEMINI_PRO_MODEL}")
    
    # Загружаем данные
    print("\n📂 Loading fresh data...")
    all_data = load_all_fresh_data()
    
    sources_loaded = sum(1 for v in all_data.values() if v)
    print(f"   Sources loaded: {sources_loaded}")
    
    # Извлекаем боли
    print("\n🔍 Extracting pain texts...")
    pain_texts = extract_pain_texts(all_data)
    print(f"   Pain texts found: {len(pain_texts)}")
    
    if not pain_texts:
        print("⚠️ No data found. Skipping analysis.")
        return []

    # Анализируем
    print("\n🧠 Analyzing with AI Pipeline...")
    top_pains = analyze_pains_with_gemini(pain_texts)
    print(f"   Categories identified: {len(top_pains)}")
    
    # Сохраняем
    if top_pains:
        save_top_pains(top_pains)
        
        print(f"\n📊 Top 3 Pain Categories:")
        for pain in top_pains[:3]:
            print(f"   🔥 {pain['category']}: {pain['frequency']} жалоб")
            print(f"      💡 {pain['business_idea'][:60]}...")
    
    return top_pains


if __name__ == "__main__":
    run()
