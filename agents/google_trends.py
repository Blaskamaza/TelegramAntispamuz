"""
Google Trends Agent — Анализ трендов Узбекистана
Использует pytrends для получения трендовых запросов

БЕСПЛАТНО: Нет явных лимитов API
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from config import GOOGLE_TRENDS_KEYWORDS, PAIN_KEYWORDS, FRESH_DIR, TODAY

# PyTrends
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("⚠️ pytrends not installed. Run: pip install pytrends")


class GoogleTrendsScanner:
    """
    Сканер трендов Google для Узбекистана.
    """
    
    def __init__(self, geo: str = "UZ", hl: str = "ru"):
        """
        Args:
            geo: Код страны (UZ = Узбекистан)
            hl: Язык (ru = русский)
        """
        self.geo = geo
        self.hl = hl
        self.pytrends = None
        
        if PYTRENDS_AVAILABLE:
            self.pytrends = TrendReq(hl=hl, tz=300)  # UTC+5 для Узбекистана
    
    def get_trending_searches(self) -> List[str]:
        """
        Получает текущие трендовые запросы в стране.
        
        Returns:
            Список трендовых запросов
        """
        if not self.pytrends:
            return self._mock_trending()
        
        try:
            # Дневные тренды (trending searches)
            trending_df = self.pytrends.trending_searches(pn='uzbekistan')
            if trending_df is not None and not trending_df.empty:
                return trending_df[0].tolist()[:20]
        except Exception as e:
            print(f"⚠️ Trending searches error: {e}")
        
        # Fallback: realtime trends
        try:
            realtime = self.pytrends.realtime_trending_searches(pn='UZ')
            if realtime is not None and not realtime.empty:
                return realtime['title'].tolist()[:20]
        except Exception as e:
            print(f"⚠️ Realtime trends error: {e}")
        
        return self._mock_trending()
    
    def get_interest_over_time(self, keywords: List[str], timeframe: str = "today 3-m") -> Dict:
        """
        Получает динамику интереса к ключевым словам.
        
        Args:
            keywords: Список ключевых слов (макс 5)
            timeframe: Период (today 3-m = 3 месяца)
        
        Returns:
            Dict с данными интереса
        """
        if not self.pytrends or not keywords:
            return {}
        
        try:
            # Берём максимум 5 ключевых слов
            kw_list = keywords[:5]
            
            self.pytrends.build_payload(
                kw_list, 
                cat=0, 
                timeframe=timeframe, 
                geo=self.geo
            )
            
            interest_df = self.pytrends.interest_over_time()
            
            if interest_df is not None and not interest_df.empty:
                # Преобразуем в dict
                result = {}
                for kw in kw_list:
                    if kw in interest_df.columns:
                        result[kw] = {
                            "avg": float(interest_df[kw].mean()),
                            "max": int(interest_df[kw].max()),
                            "trend": "rising" if interest_df[kw].iloc[-1] > interest_df[kw].iloc[0] else "falling"
                        }
                return result
                
        except Exception as e:
            print(f"⚠️ Interest over time error: {e}")
        
        return {}
    
    def get_related_topics(self, keyword: str) -> Dict:
        """
        Получает связанные темы для ключевого слова.
        
        Returns:
            Dict с rising и top темами
        """
        if not self.pytrends:
            return {}
        
        try:
            self.pytrends.build_payload([keyword], geo=self.geo)
            related = self.pytrends.related_topics()
            
            result = {"rising": [], "top": []}
            
            if keyword in related:
                data = related[keyword]
                
                if 'rising' in data and data['rising'] is not None:
                    result["rising"] = data['rising']['topic_title'].tolist()[:10]
                    
                if 'top' in data and data['top'] is not None:
                    result["top"] = data['top']['topic_title'].tolist()[:10]
            
            return result
            
        except Exception as e:
            print(f"⚠️ Related topics error: {e}")
            return {}
    
    def get_related_queries(self, keyword: str) -> Dict:
        """
        Получает связанные запросы для ключевого слова.
        """
        if not self.pytrends:
            return {}
        
        try:
            self.pytrends.build_payload([keyword], geo=self.geo)
            related = self.pytrends.related_queries()
            
            result = {"rising": [], "top": []}
            
            if keyword in related:
                data = related[keyword]
                
                if 'rising' in data and data['rising'] is not None:
                    result["rising"] = data['rising']['query'].tolist()[:10]
                    
                if 'top' in data and data['top'] is not None:
                    result["top"] = data['top']['query'].tolist()[:10]
            
            return result
            
        except Exception as e:
            print(f"⚠️ Related queries error: {e}")
            return {}
    
    def _mock_trending(self) -> List[str]:
        """Mock данные для тестирования"""
        return [
            "работа в ташкенте",
            "курс доллара узбекистан",
            "DTM 2026 результаты",
            "iPhone цена Узбекистан",
            "фриланс для начинающих",
            "бизнес идеи 2026",
            "IT курсы ташкент",
            "квартира аренда ташкент",
            "кредит без отказа",
            "английский язык курсы",
        ]


def extract_pains_from_trends(trends: List[str], keywords: List[str]) -> List[Dict]:
    """
    Извлекает боли из трендов.
    
    Args:
        trends: Список трендовых запросов
        keywords: Список болевых ключевых слов
    
    Returns:
        Список найденных болей
    """
    pains = []
    
    for trend in trends:
        trend_lower = trend.lower()
        matched_keywords = []
        
        for kw in keywords:
            if kw in trend_lower:
                matched_keywords.append(kw)
        
        if matched_keywords:
            pains.append({
                "text": trend,
                "type": "trend",
                "keywords": matched_keywords,
                "score": len(matched_keywords),
            })
    
    return sorted(pains, key=lambda x: x["score"], reverse=True)


def save_trends_data(data: Dict) -> Path:
    """Сохраняет данные трендов"""
    output_dir = FRESH_DIR / "trends"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"uz_{TODAY}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved trends data to {output_file}")
    return output_file


def run():
    """Основная функция агента"""
    print("📈 Google Trends Agent starting...")
    print(f"📅 Date: {TODAY}")
    print(f"🌍 Region: UZ (Uzbekistan)")
    print(f"🔑 PyTrends: {'✅' if PYTRENDS_AVAILABLE else '❌ Mock'}")
    
    scanner = GoogleTrendsScanner(geo="UZ", hl="ru")
    
    # 1. Трендовые запросы
    print("\n🔍 Getting trending searches...")
    trending = scanner.get_trending_searches()
    print(f"   Found {len(trending)} trends")
    
    # 2. Интерес к ключевым словам
    print("\n📊 Analyzing interest over time...")
    interest = scanner.get_interest_over_time(GOOGLE_TRENDS_KEYWORDS[:5])
    for kw, data in interest.items():
        print(f"   {kw}: avg={data.get('avg', 0):.1f}, trend={data.get('trend', 'n/a')}")
    
    # 3. Связанные запросы для топ ключевых слов
    print("\n🔗 Getting related queries...")
    related = {}
    for kw in GOOGLE_TRENDS_KEYWORDS[:3]:  # Только первые 3 для экономии
        related[kw] = scanner.get_related_queries(kw)
        if related[kw].get("rising"):
            print(f"   {kw}: {len(related[kw]['rising'])} rising queries")
    
    # 4. Извлечение болей
    print("\n💊 Extracting pains from trends...")
    pains = extract_pains_from_trends(trending, PAIN_KEYWORDS)
    print(f"   Found {len(pains)} pains")
    
    # Собираем результаты
    all_data = {
        "date": TODAY,
        "region": "UZ",
        "trending_searches": trending,
        "interest_over_time": interest,
        "related_queries": related,
        "pains_found": len(pains),
        "pains": pains,
    }
    
    print(f"\n{'='*50}")
    print(f"📊 Results:")
    print(f"   Trending: {len(trending)}")
    print(f"   Keywords analyzed: {len(interest)}")
    print(f"   Pains found: {len(pains)}")
    print(f"{'='*50}")
    
    save_trends_data(all_data)
    return all_data


if __name__ == "__main__":
    run()
