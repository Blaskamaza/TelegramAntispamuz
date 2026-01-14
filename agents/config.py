"""
UZ AI Factory — Конфигурация
Все бесплатные источники данных для узбекского рынка
"""

import os
from datetime import datetime
from pathlib import Path

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
    "учёба в вузах узбекистана",
    "домашний бизнес идеи",
    "онлайн работа узбекистан",
    "фриланс узбекистан",
    "IT курсы ташкент",
]

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
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyB4wHZE-CbHK95TZhYiHsiMcMlFhP9nq58")
GEMINI_PRO_MODEL = "gemini-3-pro-preview"
GEMINI_FLASH_MODEL = "gemini-3-flash-preview"
GEMINI_LITE_MODEL = "gemini-2.5-flash-lite"

# Rate Limits (Tier 1 Paid)
GEMINI_RPM = 60       # Requests Per Minute
GEMINI_TPM = 1000000  # Tokens Per Minute
GEMINI_RPD = 1000     # Requests Per Day

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
