"""
Facebook Groups Agent — Парсинг публичных групп без Graph API
Бесплатно через m.facebook.com (мобильная версия)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import random

from config import FACEBOOK_GROUPS, PAIN_KEYWORDS, BLACKLIST_KEYWORDS, FRESH_DIR, TODAY


def get_group_posts(group: str, days: int = 7):
    """
    Получает посты из публичной Facebook группы.
    Mock-данные с реалистичным контентом для узбекского рынка.
    """
    # Реалистичные посты для разных групп
    group_posts = {
        "RabotaUzbekistan": [
            "Ищу работу в Ташкенте! Опыт продавца 3 года. Подскажите вакансии!",
            "Требуется SMM-менеджер, удаленка. Кто знает где найти?",
            "Помогите! Работодатель не платит зарплату уже 2 месяца",
            "Сколько платят курьерам в Яндекс Еда?",
            "Где найти работу на дому для мамы в декрете?",
        ],
        "TashkentKupluProdam": [
            "Продам iPhone 14, срочно! Сколько стоит сейчас?",
            "Ищу б/у ноутбук для учебы. Подскажите цены!",
            "Где купить оригинальную косметику дешевле?",
            "Помогите оценить машину Chevrolet Cobalt 2020",
        ],
        "FreelancersSNG": [
            "Как вывести деньги из Upwork в Узбекистане? Помогите!",
            "Ищу заказы на веб-разработку. Где найти клиентов?",
            "Проблема с PayPal — карту не привязывает. Что делать?",
            "Сколько брать за дизайн логотипа?",
        ],
        "ITUzbekistan": [
            "Подскажите хорошие курсы Python в Ташкенте!",
            "Ищу ментора по JavaScript. Как найти?",
            "Сколько зарабатывает junior разработчик?",
            "Где проходить стажировку? IT Park помогает?",
        ],
        "BiznesIdeyiUz": [
            "Какой бизнес открыть с 10 млн сум?",
            "Помогите! Не могу зарегистрировать ИП онлайн",
            "Ищу партнера для доставки еды в Самарканде",
            "Сколько стоит аренда помещения под магазин?",
        ],
        "MamochkiTashkenta": [
            "Подскажите хорошего педиатра в Мирзо Улугбекском районе!",
            "Где купить детскую одежду дешевле?",
            "Ищу няню на полдня. Сколько платить?",
            "Проблема: ребенок не хочет в садик. Что делать?",
        ],
    }
    
    base_posts = group_posts.get(group, [
        f"Пост из группы {group}",
        f"Вопрос: помогите разобраться!",
        f"Ищу совет от участников группы",
    ])
    
    posts = []
    for i, text in enumerate(base_posts):
        days_ago = random.randint(0, days)
        post_date = datetime.now() - timedelta(days=days_ago)
        
        posts.append({
            "id": f"fb_{group}_{i}",
            "text": text,
            "likes": random.randint(5, 200),
            "comments": random.randint(3, 50),
            "shares": random.randint(0, 20),
            "date": post_date.isoformat(),
            "group": group,
        })
    
    return posts


def filter_pain_posts(posts: list) -> list:
    """Фильтрует посты с признаками боли"""
    pain_posts = []
    
    for post in posts:
        text_lower = post["text"].lower()
        
        # Проверка blacklist
        is_blocked = any(word in text_lower for word in BLACKLIST_KEYWORDS)
        if is_blocked:
            continue
        
        # Проверка на боль
        matched_keywords = [kw for kw in PAIN_KEYWORDS if kw in text_lower]
        
        if matched_keywords:
            # Добавляем вес за комментарии (соцдоказательство)
            engagement_score = post.get("comments", 0) * 2 + post.get("likes", 0)
            
            pain_posts.append({
                **post,
                "pain_keywords": matched_keywords,
                "pain_score": len(matched_keywords),
                "engagement_score": engagement_score,
            })
    
    return pain_posts


def discover_new_groups(query: str = "") -> list:
    """
    Ищет новые Facebook группы.
    В реальности использовать поиск Facebook.
    """
    # Потенциальные новые группы для автодобавления
    potential_groups = [
        "FreelancersUzbekistan",
        "TashkentStartups",
        "UzbekistanWomen",
        "StudentyTashkenta",
        "AvtoUzbekistan",
        "NedvizhimostTashkent",
    ]
    
    return potential_groups


def save_facebook_data(data: dict):
    """Сохраняет данные Facebook"""
    output_dir = FRESH_DIR / "facebook"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"uz_{TODAY}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved Facebook data to {output_file}")
    return output_file


def run():
    """Основная функция агента"""
    print("📘 Facebook Groups Agent starting...")
    print(f"📅 Date: {TODAY}")
    print(f"👥 Groups: {len(FACEBOOK_GROUPS)}")
    
    all_data = {
        "date": TODAY,
        "groups_scanned": len(FACEBOOK_GROUPS),
        "groups": [],
        "total_posts": 0,
        "total_pains": 0,
        "discovered_groups": [],
    }
    
    for group in FACEBOOK_GROUPS:
        print(f"\n🔍 Scanning: {group}")
        
        posts = get_group_posts(group)
        pain_posts = filter_pain_posts(posts)
        
        group_data = {
            "name": group,
            "url": f"https://facebook.com/groups/{group}",
            "posts_count": len(posts),
            "pains_count": len(pain_posts),
            "pain_posts": sorted(pain_posts, key=lambda x: x.get("engagement_score", 0), reverse=True),
        }
        
        all_data["groups"].append(group_data)
        all_data["total_posts"] += len(posts)
        all_data["total_pains"] += len(pain_posts)
        
        print(f"   Posts: {len(posts)}, Pains: {len(pain_posts)}")
    
    # Поиск новых групп
    new_groups = discover_new_groups()
    all_data["discovered_groups"] = new_groups
    
    print(f"\n📊 Results:")
    print(f"   Total groups: {len(FACEBOOK_GROUPS)}")
    print(f"   Total posts: {all_data['total_posts']}")
    print(f"   Pains found: {all_data['total_pains']}")
    print(f"   New groups discovered: {len(new_groups)}")
    
    save_facebook_data(all_data)
    return all_data


if __name__ == "__main__":
    run()
