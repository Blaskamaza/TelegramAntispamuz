# === 50 ПРОВЕРЕННЫХ TELEGRAM КАНАЛОВ УЗБЕКИСТАНА ===
# Обновлено: 14 января 2026
# Источники: TGStat, UzTelegram, web search
# Статус: ВСЕ ПРОВЕРЕНЫ - работают на момент обновления

TELEGRAM_CHANNELS = [
    # ========== НОВОСТИ (топ, 1M+ подписчиков) ==========
    "@kunuz",                   # KUN.UZ RASMIY - 3M+ (ПРОВЕРЕН)
    "@gazetauz",                # Gazeta.uz - новости (ПРОВЕРЕН, 22 поста)
    "@daryouz",                 # DARYO RASMIY 
    "@spotuz",                  # Spot.uz - бизнес и технологии (ПРОВЕРЕН, 30 постов)
    "@reloaded_uz",             # Repost.uz новости
    
    # ========== РАБОТА И ВАКАНСИИ ==========
    "@rabota_uzbekistan",       # RABOTA.UZ - главный (ПРОВЕРЕН)
    "@uzbekistanwork",          # Работа в Ташкенте (ПРОВЕРЕН)
    "@bestjobuz",               # Выбери работу (ПРОВЕРЕН, 8 постов)
    "@itmarket_uz",             # IT Market от IT Park (ОФИЦИАЛЬНЫЙ!)
    "@ITjobs_Uzbekistan",       # IT вакансии (ПРОВЕРЕН)
    "@ITresume_Uzbekistan",     # IT резюме (ПРОВЕРЕН)
    "@tashkent_vakansii",       # Вакансии Ташкент (ПРОВЕРЕН)
    "@ishor_vakansiya",         # Ish bor vakansiya
    "@buxoroda_ish_bor",        # Bukhara jobs
    "@xorazm_ish",              # Khorezm jobs
    
    # ========== IT И ПРОГРАММИРОВАНИЕ ==========
    "@joshdeveloper",           # JoshDeveloper (ПРОВЕРЕН, 6 постов)
    "@frontenduz",              # Frontend UZ (ПРОВЕРЕН)
    "@pythonuz",                # Python Uzbekistan (ПРОВЕРЕН)
    "@devuz",                   # Dev UZ (ПРОВЕРЕН)
    "@androiduz",               # Android UZ (ПРОВЕРЕН)
    "@backenduz",               # Backend UZ (ПРОВЕРЕН)
    "@mohirdev",                # Mohirdev - IT образование
    "@uzcoder",                 # UZ Coder
    
    # ========== ОБРАЗОВАНИЕ ==========
    "@uzedu",                   # Xalq ta'limi vazirligi (ПРОВЕРЕН, 11 постов)
    "@eduuz",                   # Oliy ta'lim vazirligi (ПРОВЕРЕН, 8 постов)
    "@talimuz",                 # Ta'lim.uz (ПРОВЕРЕН, 8 постов)
    "@rasmiydtm",               # DTM RASMIY - ОФИЦИАЛЬНЫЙ!
    "@abituriyentuz",           # Abituriyentlar (ПРОВЕРЕН, 1 пост)
    "@erasmus_uz",              # Erasmus+ Uzbekistan (ПРОВЕРЕН, 13 постов)
    "@ubtuit_uz",               # TUIT - университет
    "@tsueuzofficial",          # TSUE - экономический университет
    "@nuu_uz",                  # NUUz - национальный университет
    "@wiut_uz",                 # Westminster University
    "@talim_obrazovaniye",      # Ta'lim / Образование
    
    # ========== БИЗНЕС И ФИНАНСЫ ==========
    "@KPTLUZ",                  # Kapital.uz - финансы (ПРОВЕРЕН, 30 постов)
    "@kredituz",                # Кредиты (ПРОВЕРЕН, 3 поста)
    "@click_uz",                # Click to'lov (ПРОВЕРЕН, 2 поста)
    "@payme_uz",                # Payme (ПРОВЕРЕН, 4 поста)
    "@humo_card",               # Humo Card (ПРОВЕРЕН)
    "@soliq_uz",                # Soliq - налоги (ПРОВЕРЕН)
    "@biznesuz",                # Biznes UZ
    
    # ========== АВТО И МАРКЕТПЛЕЙС ==========
    "@moshina_bozor",           # MOSHINA BOZOR (ПРОВЕРЕН, 22 поста)
    "@olx_uzbekistan",          # OLX Uzbekistan (ПРОВЕРЕН, 3 поста)
    "@avtoelon_rasmiy",         # Avtoelon rasmiy
    
    # ========== НЕДВИЖИМОСТЬ ==========
    "@kvartira_tashkent",       # Kvartiralar Toshkent (ПРОВЕРЕН)
    "@arenda_tashkent",         # Arenda Tashkent (ПРОВЕРЕН)
    
    # ========== ДРУГОЕ ==========
    "@travel_uzbekistan",       # Travel UZ (ПРОВЕРЕН)
    "@ingliz_tili_uz",          # Ingliz tili (ПРОВЕРЕН)
]

# Количество каналов для сканирования за один запуск
TELEGRAM_SCAN_LIMIT = 30  # Чтобы избежать FloodWait

# Пауза между каналами (секунды)
TELEGRAM_DELAY = 1.5

# Список нерабочих каналов (для исключения)
BROKEN_CHANNELS = [
    "@darlouz",           # Ошибка: No user
    "@nuz_uz",            # unacceptable username
    "@it_park_uzbekistan",# unacceptable
    "@startup_chayhana",  # No user
    "@uzbekcoders",       # unacceptable
    "@datascienceuz",     # unacceptable
    "@dtm_rasmiy",        # unacceptable
    "@biznes_uz",         # unacceptable
    "@eastfruit_uz",      # No user
    "@talim_uz",          # unacceptable
    "@abituriyent_uz",    # unacceptable
    "@wiut_official",     # unacceptable
    "@matematika_uz",     # unacceptable
    "@startup_uz",        # unacceptable
    "@tadbirkoruz",       # unacceptable
    "@bankuz",            # No user
    "@uzcard_rasmiy",     # No user
    "@uy_joy_uz",         # unacceptable
    "@shifokor_uz",       # unacceptable
    "@apteka_uz",         # No user
    "@turizm_uz",         # unacceptable

    # === AUTO-DISCOVERED ===
    "@uzauto_official",  # AUTO-DISCOVERED 2026-01-14
    "@python_uz",  # AUTO-DISCOVERED 2026-01-14
    "@javascript_uzb",  # AUTO-DISCOVERED 2026-01-14
    "@inha_uz",  # AUTO-DISCOVERED 2026-01-14
    "@nodejs_uz",  # AUTO-DISCOVERED 2026-01-14
    "@bank_vakansiy",  # AUTO-DISCOVERED 2026-01-14
    "@laravel_uz",  # AUTO-DISCOVERED 2026-01-14
    "@AgrobankChannel",  # AUTO-DISCOVERED 2026-01-14
    "@InvestinUzb",  # AUTO-DISCOVERED 2026-01-14
    "@kapital24",  # AUTO-DISCOVERED 2026-01-14
    "@rustlanguz",  # AUTO-DISCOVERED 2026-01-14
    "@Uybor",  # AUTO-DISCOVERED 2026-01-14
    "@vtavto",  # AUTO-DISCOVERED 2026-01-14
    "@typescript_uzb",  # AUTO-DISCOVERED 2026-01-14
    "@htbuz",  # AUTO-DISCOVERED 2026-01-14
    "@wiut_official_telegram",  # AUTO-DISCOVERED 2026-01-14
    "@ipakyulibankuz",  # AUTO-DISCOVERED 2026-01-14
    "@ziglang_uz",  # AUTO-DISCOVERED 2026-01-14
    "@bank_asaka",  # AUTO-DISCOVERED 2026-01-14
    "@kvartiri_v_tashkente",  # AUTO-DISCOVERED 2026-01-14
    "@js_uzb",  # AUTO-DISCOVERED 2026-01-14
    "@ziraatbankuzbekistan",  # AUTO-DISCOVERED 2026-01-14
    "@podrabotka_vakansiiiz",  # AUTO-DISCOVERED 2026-01-14
    "@sqbuz",  # AUTO-DISCOVERED 2026-01-14
    "@KlyuchiTashkentaArenda",  # AUTO-DISCOVERED 2026-01-14
    "@freelance_uzb",  # AUTO-DISCOVERED 2026-01-14

    # === AUTO-DISCOVERED ===
    "@ITEducationAssociation",  # AUTO-DISCOVERED 2026-01-14
    "@freelancer_uzbek",  # AUTO-DISCOVERED 2026-01-14
    "@react_uz",  # AUTO-DISCOVERED 2026-01-14
    "@tashkent_segodnya",  # AUTO-DISCOVERED 2026-01-14
    "@startupchoyxona",  # AUTO-DISCOVERED 2026-01-14
    "@Hamkorbankuz",  # AUTO-DISCOVERED 2026-01-14
    "@asiaalliancebank",  # AUTO-DISCOVERED 2026-01-14
    "@uzdev_jobs",  # AUTO-DISCOVERED 2026-01-14
    "@uyborbot",  # AUTO-DISCOVERED 2026-01-14
    "@RealUzbekistan",  # AUTO-DISCOVERED 2026-01-14
    "@kvartira_dom_arenda",  # AUTO-DISCOVERED 2026-01-14
    "@avtoelon",  # AUTO-DISCOVERED 2026-01-14
    "@avtomarket_uzbekistan",  # AUTO-DISCOVERED 2026-01-14
    "@headhunter_uz",  # AUTO-DISCOVERED 2026-01-14
    "@ravnaqbank",  # AUTO-DISCOVERED 2026-01-14
    "@xalqbankinfo",  # AUTO-DISCOVERED 2026-01-14
    "@test_uz_ru",  # AUTO-DISCOVERED 2026-01-14
    "@aloqabank",  # AUTO-DISCOVERED 2026-01-14
    "@kursy_uz",  # AUTO-DISCOVERED 2026-01-14
    "@turonbankuz",  # AUTO-DISCOVERED 2026-01-14
    "@davrbankuz",  # AUTO-DISCOVERED 2026-01-14
    "@rabotay",  # AUTO-DISCOVERED 2026-01-14
    "@frilansso",  # AUTO-DISCOVERED 2026-01-14
    "@mikrokreditbank",  # AUTO-DISCOVERED 2026-01-14
    "@savdogarbank",  # AUTO-DISCOVERED 2026-01-14
    "@uzbekvc",  # AUTO-DISCOVERED 2026-01-14
]
