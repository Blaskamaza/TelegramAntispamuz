"""
Scout Agent — Alibaba Function Compute
Узел «Scouting & Intelligence»

Запускается каждые 4 часа через Cron-триггер.
Использует Redis для Task Queue (дедупликация).
Лимит: 1M запросов/мес (6 запросов/4ч = ~1300/мес)
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# Alibaba FC SDK
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scout_agent")


# ============================================================
# REDIS TASK QUEUE
# ============================================================

class TaskQueue:
    """
    Redis-based Task Queue для дедупликации работы агентов.
    Использует ApsaraDB for Redis Free Tier (256MB).
    """
    
    def __init__(self, host: str, port: int, password: str, db: int = 0):
        self.redis_client = None
        if REDIS_AVAILABLE and host:
            try:
                self.redis_client = redis.Redis(
                    host=host,
                    port=port,
                    password=password,
                    db=db,
                    decode_responses=True,
                    socket_timeout=5,
                )
                self.redis_client.ping()
                logger.info("✅ Redis connected")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}")
                self.redis_client = None
    
    def _generate_task_id(self, task_type: str, data: dict) -> str:
        """Генерирует уникальный ID задачи"""
        content = f"{task_type}:{json.dumps(data, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def add_task(self, task_type: str, data: dict, ttl_hours: int = 24) -> bool:
        """
        Добавляет задачу в очередь.
        Возвращает True если задача новая, False если дубликат.
        """
        if not self.redis_client:
            return True  # Без Redis всегда выполняем
        
        task_id = self._generate_task_id(task_type, data)
        key = f"task:{task_type}:{task_id}"
        
        # Проверяем существование
        if self.redis_client.exists(key):
            logger.info(f"⏭️ Task already exists: {task_id}")
            return False
        
        # Добавляем с TTL
        self.redis_client.setex(
            key,
            timedelta(hours=ttl_hours),
            json.dumps({
                "data": data,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            })
        )
        logger.info(f"✅ Task added: {task_id}")
        return True
    
    def complete_task(self, task_type: str, data: dict):
        """Помечает задачу как выполненную"""
        if not self.redis_client:
            return
        
        task_id = self._generate_task_id(task_type, data)
        key = f"task:{task_type}:{task_id}"
        
        if self.redis_client.exists(key):
            task = json.loads(self.redis_client.get(key))
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            self.redis_client.setex(key, timedelta(hours=48), json.dumps(task))
    
    def get_pending_count(self, task_type: str) -> int:
        """Количество ожидающих задач"""
        if not self.redis_client:
            return 0
        
        pattern = f"task:{task_type}:*"
        count = 0
        for key in self.redis_client.scan_iter(pattern):
            task = json.loads(self.redis_client.get(key))
            if task.get("status") == "pending":
                count += 1
        return count


# ============================================================
# TREND SOURCES
# ============================================================

TREND_SOURCES = [
    # Google Trends — без API
    {"type": "google_trends", "region": "UZ", "keywords": [
        "работа на дому", "фриланс", "онлайн заработок",
        "DTM подготовка", "IT курсы", "кредит онлайн",
    ]},
    # YouTube — API free tier
    {"type": "youtube", "region": "UZ", "queries": [
        "qanday pul ishlash", "biznes g'oyalar",
    ]},
    # Telegram — public channels
    {"type": "telegram", "channels": [
        "@tashkent_help", "@ishbilish", "@freelanceuz",
    ]},
]


# ============================================================
# PAIN CLASSIFIER (Gemini)
# ============================================================

class PainClassifier:
    """
    Классификатор болей с использованием Gemini 1.5 Flash.
    Оптимизирован для минимального потребления токенов.
    """
    
    SYSTEM_PROMPT = """You are a market researcher for Uzbekistan.
Analyze the text and extract user pains that could be monetized.
Return JSON: {"pains": [{"text": "...", "category": "...", "score": 1-10}]}
Categories: work, education, finance, tech, health, housing, shopping, family
Be very brief. Max 5 pains per request."""

    def __init__(self, api_key: str):
        self.model = None
        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini connected")
            except Exception as e:
                logger.warning(f"⚠️ Gemini init failed: {e}")
    
    def classify(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Классифицирует тексты и извлекает боли"""
        if not self.model or not texts:
            return []
        
        # Объединяем тексты для экономии токенов
        combined = "\n---\n".join(texts[:10])  # Макс 10 за раз
        
        try:
            response = self.model.generate_content(
                f"{self.SYSTEM_PROMPT}\n\nTexts:\n{combined}",
                generation_config={
                    "max_output_tokens": 256,
                    "temperature": 0.3,
                }
            )
            
            # Парсим JSON из ответа
            result = json.loads(response.text)
            return result.get("pains", [])
        except Exception as e:
            logger.error(f"❌ Gemini classify error: {e}")
            return []


# ============================================================
# MAIN HANDLER (Alibaba Function Compute)
# ============================================================

def handler(event, context):
    """
    Alibaba Function Compute Handler
    
    Триггер: Cron каждые 4 часа
    Лимит памяти: 128MB
    Таймаут: 60 сек
    """
    logger.info("🚀 Scout Agent started")
    start_time = datetime.now()
    
    # Конфигурация из окружения
    import os
    redis_host = os.getenv("REDIS_HOST", "")
    redis_password = os.getenv("REDIS_PASSWORD", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    
    # Инициализация
    queue = TaskQueue(redis_host, 6379, redis_password)
    classifier = PainClassifier(gemini_key)
    
    results = {
        "timestamp": start_time.isoformat(),
        "sources_processed": 0,
        "pains_found": 0,
        "tasks_created": 0,
    }
    
    # Обработка источников
    for source in TREND_SOURCES:
        source_type = source["type"]
        logger.info(f"📡 Processing: {source_type}")
        
        # Проверяем, не обрабатывали ли уже
        if not queue.add_task("scan", {"source": source_type, "date": start_time.strftime("%Y-%m-%d")}):
            logger.info(f"⏭️ Skipping (already processed): {source_type}")
            continue
        
        # Сбор данных (mock для примера)
        texts = collect_data_from_source(source)
        
        # Классификация болей
        if texts:
            pains = classifier.classify(texts)
            results["pains_found"] += len(pains)
            
            # Создаем задачи для следующих этапов
            for pain in pains:
                if pain.get("score", 0) >= 7:  # Только высокий скор
                    if queue.add_task("analyze", {"pain": pain["text"], "category": pain.get("category")}):
                        results["tasks_created"] += 1
        
        queue.complete_task("scan", {"source": source_type, "date": start_time.strftime("%Y-%m-%d")})
        results["sources_processed"] += 1
    
    # Финализация
    duration = (datetime.now() - start_time).total_seconds()
    results["duration_sec"] = duration
    
    logger.info(f"✅ Scout Agent completed in {duration:.2f}s")
    logger.info(f"📊 Results: {json.dumps(results)}")
    
    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }


def collect_data_from_source(source: dict) -> List[str]:
    """Собирает данные из источника (mock для примера)"""
    source_type = source["type"]
    
    # В реальности здесь вызовы API
    mock_data = {
        "google_trends": [
            "работа на дому в ташкенте",
            "как заработать фрилансом",
            "подготовка к DTM бесплатно",
        ],
        "youtube": [
            "помогите найти работу",
            "где взять кредит без отказа",
        ],
        "telegram": [
            "ищу репетитора по математике",
            "подскажите хорошего врача",
        ],
    }
    
    return mock_data.get(source_type, [])


# ============================================================
# LOCAL TESTING
# ============================================================

if __name__ == "__main__":
    # Локальный тест
    import os
    os.environ["REDIS_HOST"] = ""
    os.environ["GEMINI_API_KEY"] = ""
    
    result = handler({}, None)
    print(json.dumps(result, indent=2))
