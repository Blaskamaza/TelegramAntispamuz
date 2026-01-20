"""
UZ AI Factory — Конфигурация
Все бесплатные источники данных для узбекского рынка
"""

import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# === ЗАГРУЗКА .ENV ===
load_dotenv()

# === ПУТИ ===
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
FRESH_DIR = DATA_DIR / "fresh"
ARCHIVE_DIR = DATA_DIR / "archive"
LOGS_DIR = BASE_DIR / "logs"
PUBLIC_DIR = BASE_DIR / "public"
PUBLIC_DATA_DIR = PUBLIC_DIR / "data"

# === ДАТА ===
TODAY = datetime.now().strftime("%Y-%m-%d")

# === GOOGLE TRENDS ЗАПРОСЫ ===
TRENDS_KEYWORDS_UZ = [
    "учёба онлайн",
    "работа на дому",
    "доставка еды",
    "подготовка к ЕНТ",
    "курсы узбекского",
    "фриланс для девушек",
    "тесты для школьников",
    "свадебные организаторы",
    "ремонт квартир Ташкент",
    "продажа одежды instagram",
    "кредит онлайн",
    "оплата коммунальных",
    "пошив платьев",
    "английский для мигрантов",
    "такси без надбавок",
    "записаться к врачу",
    "заказ справок",
    "онлайн-переводчик",
    "QR-меню ресторан",
    "IT курсы для девочек",
]

TRENDS_KEYWORDS_UZ_LATIN = [
    "qanday pul ishlash",
    "onlayn ish",
    "yetkazib berish xizmati",
    "DTM test",
    "ingliz tili kurslari",
    "frilanser bo'lish",
    "dasturlash o'rganish",
    "biznes g'oyalar",
]

# === GOOGLE TRENDS KEYWORDS ===
GOOGLE_TRENDS_KEYWORDS = [
    "работа ташкент",
    "IT курсы",
    "фриланс",
    "бизнес идеи",
    "DTM результаты",
]

# === VK API ===
VK_SERVICE_KEY = os.getenv("VK_SERVICE_KEY", "")

# === YOUTUBE API ===
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# === YOUTUBE ЗАПРОСЫ ===
YOUTUBE_QUERIES = [
    "qanday pul ishlash",
    "как заработать в Ташкенте",
    "учёба в вузах узбекистана",
    "домашний бизнес идеи",
    "онлайн работа узбекистан",
    "фриланс узбекистан",
    "IT курсы ташкент",
]

# === PERPLEXITY API ===
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = "sonar"

# === TELEGRAM API (Telethon) ===
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "33678302"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "cd3b3aa8c05eb14f7004d314ff48daa2")
TELEGRAM_SESSION_NAME = "uz_ai_factory"

# === TELEGRAM КАНАЛЫ (50+ ПРОВЕРЕННЫХ КАНАЛОВ) ===
# Импорт из отдельного файла для удобства редактирования
try:
    from telegram_channels import TELEGRAM_CHANNELS, TELEGRAM_SCAN_LIMIT, TELEGRAM_DELAY
except ImportError:
    # Fallback если файл не найден
    TELEGRAM_CHANNELS = [
        "@kun_uz", "@gazetauz", "@spotuz", "@moshina_bozor",
        "@rabota_uzbekistan", "@bestjobuz", "@kredituz",
    ]
    TELEGRAM_SCAN_LIMIT = 20
    TELEGRAM_DELAY = 1.5

# === FACEBOOK ГРУППЫ ===
FACEBOOK_GROUPS = [
    "RabotaUzbekistan",
    "TashkentKupluProdam",
    "FreelancersSNG",
    "ITUzbekistan",
    "BiznesIdeyiUz",
    "MamochkiTashkenta",
]

# === RSS ИСТОЧНИКИ ===
RSS_FEEDS = [
    "https://daryo.uz/ru/rss",
    "https://kun.uz/rss",
    "https://gazeta.uz/rss",
    "https://repost.uz/rss",
]

# === ФИЛЬТРЫ ===
PAIN_KEYWORDS = [
    "?",
    "помогите",
    "где",
    "сколько стоит",
    "ищу",
    "нужен",
    "подскажите",
    "как",
    "проблема",
    "не работает",
    "yordam",
    "qanday",
    "qayerda",
    "kerak",
]

# === BLACKLIST (политика/религия) ===
BLACKLIST_KEYWORDS = [
    "выборы",
    "президент",
    "оппозиция",
    "протест",
    "мечеть",
    "хиджаб",
    "религия",
    "партия",
]

# === GEMINI CONFIG ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_PRO_MODEL = "gemini-2.0-flash"
GEMINI_FLASH_MODEL = "gemini-2.0-flash-lite-preview"
GEMINI_LITE_MODEL = "gemini-2.0-flash-lite-preview"

# Rate Limits (Tier 1 Paid)
GEMINI_RPM = 60       # Requests Per Minute
GEMINI_TPM = 1000000  # Tokens Per Minute
GEMINI_RPD = 1000     # Requests Per Day

# === VERTEX AI CONFIG ===
VERTEX_PROJECT_ID = os.getenv("VERTEX_PROJECT_ID", "nodal-reserve-471921-n1")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", str(BASE_DIR / "credentials.json"))

# Agent Builder RAG (Data Store создан через setup_gcp.py)
DATA_STORE_ID = os.getenv("DATA_STORE_ID", "uz-factory-knowledge")

# === GOOGLE CUSTOM SEARCH (for Smart Collector) ===
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "AIzaSyAyN1DEGhnOR66bDP9bPLDgP5ORXIGwCps")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "b11cbf6e634d440e4")

# === SUPABASE CONFIG ===
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# === GITHUB CONFIG ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# === HUGGINGFACE CONFIG ===
HF_TOKEN = os.getenv("HF_TOKEN", "")

# === N8N CONFIG ===
N8N_API_URL = os.getenv("N8N_API_URL", "http://localhost:5678")
N8N_TEMPLATES_API = "https://api.n8n.io/api/templates"

GEMINI_SYSTEM_PROMPT = """
Ты — маркетолог стартапа в Узбекистане. Анализируй данные и выдели самые частые боли пользователей, за которые они готовы платить до 50 000 сум/мес (~$4).
Формат ответа:
{
  "pain": "описание боли",
  "frequency": число упоминаний,
  "source": "Google/YouTube/Telegram/Facebook/RSS",
  "potential_price": "X000 сум",
  "business_idea": "краткая идея MVP"
}
"""
