"""
UZ AI Factory — Главный раннер всех агентов
Запускает все агенты последовательно и собирает результаты
"""

import sys
from pathlib import Path
from datetime import datetime

# Добавляем путь к агентам
sys.path.insert(0, str(Path(__file__).parent))

from config import TODAY, BASE_DIR


def log_action(action: str, status: str = "✅"):
    """Записывает действие в журнал"""
    log_file = BASE_DIR / "logs" / "journal.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"| {timestamp} | {status} | {action} |\n")


def run_all_agents():
    """Запускает все агенты последовательно"""
    print("=" * 60)
    print("🚀 UZ AI FACTORY — Starting All Agents")
    print(f"📅 Date: {TODAY}")
    print("=" * 60)
    
    # Инициализируем журнал
    log_file = BASE_DIR / "logs" / "journal.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"# 📝 Дневник Агентов — {TODAY}\n\n")
        f.write("| Время | Статус | Действие |\n")
        f.write("|-------|--------|----------|\n")
    
    results = {}
    
    # 1. Google Trends
    try:
        print("\n" + "=" * 40)
        log_action("Запуск Google Trends Agent")
        from google_trends import run as run_trends
        results["trends"] = run_trends()
        log_action("Google Trends завершен")
    except Exception as e:
        log_action(f"Google Trends ошибка: {e}", "❌")
        print(f"❌ Trends error: {e}")
    
    # 2. YouTube
    try:
        print("\n" + "=" * 40)
        log_action("Запуск YouTube Scanner")
        from youtube_scanner import run as run_youtube
        results["youtube"] = run_youtube()
        log_action("YouTube Scanner завершен")
    except Exception as e:
        log_action(f"YouTube ошибка: {e}", "❌")
        print(f"❌ YouTube error: {e}")
    
    # 3. Telegram
    try:
        print("\n" + "=" * 40)
        log_action("Запуск Telegram Scanner")
        from tg_scanner import run as run_telegram
        results["telegram"] = run_telegram()
        log_action("Telegram Scanner завершен")
    except Exception as e:
        log_action(f"Telegram ошибка: {e}", "❌")
        print(f"❌ Telegram error: {e}")
    
    # 4. Facebook
    try:
        print("\n" + "=" * 40)
        log_action("Запуск Facebook Groups Agent")
        from fb_groups import run as run_facebook
        results["facebook"] = run_facebook()
        log_action("Facebook Groups завершен")
    except Exception as e:
        log_action(f"Facebook ошибка: {e}", "❌")
        print(f"❌ Facebook error: {e}")
    
    # 5. RSS
    try:
        print("\n" + "=" * 40)
        log_action("Запуск RSS Scraper")
        from rss_scraper import run as run_rss
        results["rss"] = run_rss()
        log_action("RSS Scraper завершен")
    except Exception as e:
        log_action(f"RSS ошибка: {e}", "❌")
        print(f"❌ RSS error: {e}")
    
    # 6. Channel Discovery
    try:
        print("\n" + "=" * 40)
        log_action("Запуск Channel Discovery Agent")
        from channel_discovery import run_discovery
        results["discover"] = run_discovery()
        log_action("Channel Discovery завершен")
    except Exception as e:
        log_action(f"Channel Discovery ошибка: {e}", "❌")
        print(f"❌ Channel Discovery error: {e}")
    
    # 7. Pain Extractor
    try:
        print("\n" + "=" * 40)
        log_action("Запуск Pain Extractor (AI анализ)")
        from pain_extractor import run as run_pain
        results["pains"] = run_pain()
        log_action("Pain Extractor завершен")
    except Exception as e:
        log_action(f"Pain Extractor ошибка: {e}", "❌")
        print(f"❌ Pain Extractor error: {e}")

    # 8. Perplexity Suite (CIS + Global)
    try:
        print("\n" + "=" * 40)
        log_action("Запуск Perplexity Suite (CIS)")
        from perplexity_suite import PerplexitySuite
        suite = PerplexitySuite(region="CIS")
        results["perplexity"] = suite.run_full_scan()
        log_action("Perplexity Suite завершен")
    except Exception as e:
        log_action(f"Perplexity Suite ошибка: {e}", "❌")
        print(f"❌ Perplexity Suite error: {e}")
    
    # Итоги
    print("\n" + "=" * 60)
    print("🏁 ALL AGENTS COMPLETED")
    print("=" * 60)
    
    log_action("Все агенты завершены", "🏁")
    
    return results


if __name__ == "__main__":
    run_all_agents()
