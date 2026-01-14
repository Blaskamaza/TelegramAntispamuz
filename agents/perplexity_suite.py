"""
🧠 Perplexity Intelligence Suite
================================
Комплексный набор AI-агентов для анализа рынка Узбекистана и СНГ.

АГЕНТЫ:
1. TrendMonitor      — мониторинг трендов (UZ + CIS)
2. PainFinder        — поиск болей и проблем
3. CompetitorAnalyzer— анализ конкурентов
4. IdeaGenerator     — генерация идей + поиск Copycats (аналогов)
5. NewsAggregator    — агрегация новостей
6. MarketResearch    — исследование рынка
7. OpportunityScanner— поиск возможностей
8. StartupValidator  — валидация идей

ИСПОЛЬЗОВАНИЕ:
    from perplexity_suite import PerplexitySuite
    
    # Для Узбекистана (по умолчанию)
    suite = PerplexitySuite()
    
    # Для СНГ
    suite_cis = PerplexitySuite(region="CIS")
    
    # Поиск успешных моделей в СНГ для копирования в Узб
    copycats = suite.ideas.find_copycats("EdTech")
"""

import json
import re
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

# Импорт конфигурации
from config import (
    PERPLEXITY_API_KEY, PERPLEXITY_MODEL,
    FRESH_DIR, TODAY, PUBLIC_DATA_DIR
)


# ============================================================
# БАЗОВЫЙ КЛИЕНТ PERPLEXITY
# ============================================================

class PerplexityBase:
    """Базовый клиент с поддержкой регионов"""
    
    API_URL = "https://api.perplexity.ai/chat/completions"
    
    def __init__(self, api_key: str = None, model: str = "sonar", region: str = "Uzbekistan"):
        self.api_key = api_key or PERPLEXITY_API_KEY
        self.model = model
        self.region = region
        
        # Настройка контекста региона
        if region == "CIS":
            self.location_context = "Uzbekistan, Kazakhstan, Russia, Kyrgyzstan, Tajikistan"
            self.sources = "local news, Telegram channels, VC.ru, Habr, Forbes.kz, Gazeta.uz"
        else:
            self.location_context = "Uzbekistan"
            self.sources = "Kun.uz, Daryo.uz, Gazeta.uz, Telegram channels, Spot.uz"
            
    def _request(
        self, 
        system_prompt: str, 
        user_query: str, 
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> Optional[str]:
        """Выполняет запрос к Perplexity API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Добавляем контекст региона в системный промпт
        enhanced_system_prompt = f"{system_prompt}\n\nTARGET REGION: {self.location_context}\nSOURCES: {self.sources}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": user_query}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
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
                print(f"   Details: {e.read().decode('utf-8')[:200]}")
            except: pass
            return None
        except Exception as e:
            print(f"⚠️ Request failed: {e}")
            return None
    
    def _parse_json(self, response: str) -> Any:
        """Парсит JSON из ответа"""
        if not response:
            return None
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match: return json.loads(json_match.group())
            array_match = re.search(r'\[[\s\S]*\]', response)
            if array_match: return json.loads(array_match.group())
        except json.JSONDecodeError:
            pass
        return {"raw": response}
    
    def _save_result(self, data: Dict, agent_name: str) -> Path:
        """Сохраняет результат"""
        region_slug = self.region.lower().replace(" ", "_")
        output_dir = FRESH_DIR / "perplexity" / region_slug / agent_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_file = output_dir / f"{timestamp}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return output_file


# ============================================================
# 1. TREND MONITOR
# ============================================================

class TrendMonitor(PerplexityBase):
    """🔥 Мониторинг трендов (UZ + CIS)"""
    
    SYSTEM_PROMPT = """You are an expert trend analyst.
TASK: Find and analyze CURRENT trending topics RIGHT NOW.
OUTPUT FORMAT (JSON):
{
    "timestamp": "YYYY-MM-DD HH:MM",
    "hot_topics": [{"topic": "...", "category": "...", "heat_score": 1-10, "source": "..."}],
    "trending_searches": ["..."],
    "viral_content": ["..."],
    "business_implications": ["..."]
}"""
    
    def get_current(self) -> Dict:
        """Получает текущие тренды"""
        query = f"""Search for what's trending in {self.location_context} RIGHT NOW.
Current timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Find top news, social media discussions, and viral topics."""
        
        print(f"🔥 TrendMonitor: Scanning trends in {self.region}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.2)
        result = self._parse_json(response)
        if result: self._save_result(result, "trends")
        return result


# ============================================================
# 2. PAIN FINDER
# ============================================================

class PainFinder(PerplexityBase):
    """💊 Поиск болей и проблем"""
    
    SYSTEM_PROMPT = """You are a customer research specialist finding REAL PROBLEMS.
TASK: Search for actual complaints, questions, and pain points people discuss online.
OUTPUT FORMAT (JSON):
{
    "pains": [
        {
            "pain": "...", "category": "...", "severity": "high/medium", 
            "source": "...", "quotes": ["..."], "business_opportunity": "..."
        }
    ],
    "total_pains_found": 0
}"""
    
    def find_all(self, limit: int = 20) -> Dict:
        """Находит боли"""
        query = f"""Research real problems people in {self.location_context} face.
Search in comments, forums, social media.
Find {limit} specific problems with quotes."""
        
        print(f"💊 PainFinder: Searching pains in {self.region}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.3)
        result = self._parse_json(response)
        if result: self._save_result(result, "pains")
        return result


# ============================================================
# 3. COMPETITOR ANALYZER
# ============================================================

class CompetitorAnalyzer(PerplexityBase):
    """📊 Анализ конкурентов"""
    
    SYSTEM_PROMPT = """You are a competitive intelligence analyst.
TASK: Analyze competitors in a specific market/niche.
OUTPUT FORMAT (JSON):
{
    "niche": "...", "market_size": "...",
    "competitors": [{"name": "...", "offerings": ["..."], "price": "...", "weaknesses": ["..."]}],
    "gaps": ["..."]
}"""
    
    def analyze(self, niche: str) -> Dict:
        """Анализирует конкурентов"""
        query = f"""Analyze competitors in: {niche} market in {self.location_context}.
Find major players, prices, and market gaps."""
        
        print(f"📊 CompetitorAnalyzer: Analyzing {niche} in {self.region}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.2)
        result = self._parse_json(response)
        if result: self._save_result(result, "competitors")
        return result


# ============================================================
# 4. IDEA GENERATOR & COPYCAT FINDER
# ============================================================

class IdeaGenerator(PerplexityBase):
    """💡 Генерация идей и поиск аналогов (Copycats)"""
    
    SYSTEM_PROMPT = """You are a startup idea generator and venture builder.
TASK: Generate viable business ideas or find successful models to copy.
OUTPUT FORMAT (JSON):
{
    "ideas": [
        {
            "name": "...", "problem": "...", "solution": "...", 
            "monetization": "...", "startup_cost": "...", "score": 1-10
        }
    ]
}"""
    
    def generate(self, focus: str = None) -> Dict:
        """Генерирует идеи"""
        focus_text = f"Focus on: {focus}" if focus else "Any promising sector"
        query = f"""Generate business ideas for {self.location_context}.
{focus_text}. Based on current trends and problems."""
        
        print(f"💡 IdeaGenerator: Generating ideas for {self.region}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.5)
        result = self._parse_json(response)
        if result: self._save_result(result, "ideas")
        return result

    def find_copycats(self, niche: str) -> Dict:
        """
        🚀 Находит успешные стартапы в СНГ/Мире, которых нет в Узбекистане.
        Это "Идеальный Результат" для венчурного строителя.
        """
        query = f"""Find successful startups in {niche} that exist in Russia, Kazakhstan, or Global markets BUT NOT in Uzbekistan yet.

TASK:
1. Identify successful business models in CIS/Global.
2. Check if they have direct competitors in Uzbekistan.
3. Propose how to adapt them for Uzbekistan.

OUTPUT FORMAT (JSON):
{{
    "niche": "{niche}",
    "copycat_opportunities": [
        {{
            "original_startup": "Name (Country)",
            "what_they_do": "Description",
            "success_metrics": "Revenue/Users",
            "why_it_will_work_in_uzbekistan": "Reasoning",
            "adaptation_strategy": "How to launch in UZ"
        }}
    ]
}}"""
        
        print(f"🚀 IdeaGenerator: Finding Copycat opportunities for {niche}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.4)
        result = self._parse_json(response)
        if result: self._save_result(result, "copycats")
        return result


# ============================================================
# 5. NEWS AGGREGATOR
# ============================================================

class NewsAggregator(PerplexityBase):
    """📰 Агрегатор новостей"""
    
    SYSTEM_PROMPT = """You are a news analyst.
TASK: Aggregate top news and analyze business impact.
OUTPUT FORMAT (JSON):
{
    "date": "...", "top_stories": [{"title": "...", "summary": "...", "impact": "..."}]
}"""
    
    def get_today(self) -> Dict:
        """Новости за сегодня"""
        query = f"""Get today's top news from {self.location_context}.
Focus on business, tech, and economy."""
        
        print(f"📰 NewsAggregator: Fetching news for {self.region}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.1)
        result = self._parse_json(response)
        if result: self._save_result(result, "news")
        return result


# ============================================================
# 6. MARKET RESEARCH
# ============================================================

class MarketResearch(PerplexityBase):
    """📈 Исследование рынка"""
    
    SYSTEM_PROMPT = """You are a market researcher.
TASK: Conduct comprehensive market research.
OUTPUT FORMAT (JSON):
{
    "market": "...", "size": "...", "players": ["..."], "trends": ["..."]
}"""
    
    def research(self, market: str) -> Dict:
        """Исследует рынок"""
        query = f"""Research {market} market in {self.location_context}.
Include size, players, and future outlook."""
        
        print(f"📈 MarketResearch: Researching {market} in {self.region}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.2)
        result = self._parse_json(response)
        if result: self._save_result(result, "research")
        return result


# ============================================================
# 7. OPPORTUNITY SCANNER
# ============================================================

class OpportunityScanner(PerplexityBase):
    """🎯 Поиск возможностей"""
    
    SYSTEM_PROMPT = """You are a business opportunity analyst.
TASK: Find untapped niches and growing markets.
OUTPUT FORMAT (JSON):
{
    "opportunities": [{"title": "...", "type": "...", "potential": "..."}]
}"""
    
    def scan(self, focus: str = None) -> Dict:
        """Сканирует возможности"""
        focus_text = f"Focus on: {focus}" if focus else "All sectors"
        query = f"""Find business opportunities in {self.location_context}.
{focus_text}. Look for high demand and low supply."""
        
        print(f"🎯 OpportunityScanner: Scanning opportunities in {self.region}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.3)
        result = self._parse_json(response)
        if result: self._save_result(result, "opportunities")
        return result


# ============================================================
# 8. STARTUP VALIDATOR
# ============================================================

class StartupValidator(PerplexityBase):
    """✅ Валидация идей"""
    
    SYSTEM_PROMPT = """You are a startup validator.
TASK: Validate business ideas with critical thinking.
OUTPUT FORMAT (JSON):
{
    "idea": "...", "score": 1-10, "verdict": "GO/NO-GO", "analysis": "..."
}"""
    
    def validate(self, idea: str) -> Dict:
        """Валидирует идею"""
        query = f"""Validate this idea for {self.location_context}: {idea}.
Check market size, competition, and risks."""
        
        print(f"✅ StartupValidator: Validating '{idea}' for {self.region}...")
        response = self._request(self.SYSTEM_PROMPT, query, temperature=0.2)
        result = self._parse_json(response)
        if result: self._save_result(result, "validations")
        return result


# ============================================================
# UNIFIED SUITE
# ============================================================

class PerplexitySuite:
    """
    🧠 Perplexity Intelligence Suite (Multi-Region)
    """
    
    def __init__(self, api_key: str = None, region: str = "Uzbekistan"):
        self.api_key = api_key or PERPLEXITY_API_KEY
        self.region = region
        
        # Init agents
        self.trends = TrendMonitor(self.api_key, region=region)
        self.pains = PainFinder(self.api_key, region=region)
        self.competitors = CompetitorAnalyzer(self.api_key, region=region)
        self.ideas = IdeaGenerator(self.api_key, region=region)
        self.news = NewsAggregator(self.api_key, region=region)
        self.research = MarketResearch(self.api_key, region=region)
        self.opportunities = OpportunityScanner(self.api_key, region=region)
        self.validator = StartupValidator(self.api_key, region=region)
    
    def run_full_scan(self) -> Dict:
        """Полный скан"""
        print(f"\n🧠 FULL SCAN START: {self.region}")
        results = {
            "timestamp": datetime.now().isoformat(),
            "region": self.region,
            "trends": self.trends.get_current(),
            "pains": self.pains.find_all(),
            "news": self.news.get_today(),
            "opportunities": self.opportunities.scan()
        }
        
        # Save
        region_slug = self.region.lower().replace(" ", "_")
        output_dir = FRESH_DIR / "perplexity" / region_slug
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"full_scan_{TODAY}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Full scan saved to {output_file}")
        
        # Save to Public Data for Frontend
        PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
        public_file = PUBLIC_DATA_DIR / "latest_perplexity.json"
        with open(public_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ Public data updated: {public_file}")
        
        return results


# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Perplexity Intelligence Suite")
    parser.add_argument("command", help="Command to run (trends, pains, ideas, copycats, full)")
    parser.add_argument("--region", default="Uzbekistan", help="Region (Uzbekistan, CIS, Global)")
    parser.add_argument("--arg", help="Additional argument (niche, idea, focus)")
    
    args = parser.parse_args()
    
    suite = PerplexitySuite(region=args.region)
    
    if args.command == "trends":
        print(json.dumps(suite.trends.get_current(), indent=2, ensure_ascii=False))
    elif args.command == "pains":
        print(json.dumps(suite.pains.find_all(), indent=2, ensure_ascii=False))
    elif args.command == "ideas":
        print(json.dumps(suite.ideas.generate(args.arg), indent=2, ensure_ascii=False))
    elif args.command == "copycats":
        # Специальная команда для поиска аналогов
        print(json.dumps(suite.ideas.find_copycats(args.arg or "IT Startups"), indent=2, ensure_ascii=False))
    elif args.command == "full":
        suite.run_full_scan()
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
