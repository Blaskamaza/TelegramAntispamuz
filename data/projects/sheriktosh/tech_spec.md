# 🏗 Technical Specification: SherikTosh

## 🏛 Architecture
```mermaid
graph TD
    User((User))
    TG[Telegram Server]
    WH[FastAPI Webhook]
    Bot[Aiogram Logic]
    DB[(Supabase PostgreSQL)]

    User -- Sends Message --> TG
    TG -- HTTPS POST --> WH
    WH -- Updates --> Bot
    Bot -- CRUD --> DB
    Bot -- Reply --> TG
    TG -- Push --> User
```

## 💾 Database Schema (ERD)
```mermaid
erDiagram
    USERS {
        bigint telegram_id PK
        string full_name
        int age
        string gender
        int budget_limit
        string district_pref
        boolean has_room
        string contact_username
        timestamp created_at
    }
    MATCHES {
        int id PK
        bigint user_a_id FK
        bigint user_b_id FK
        timestamp match_date
    }
```

## 🛠 Tech Stack
- **Frontend:** Telegram Interface (Aiogram 3.x)
- **Backend:** Python 3.11, FastAPI (Webhook Handler)
- **Database:** PostgreSQL (Supabase via AsyncSQLAlchemy)
- **Infrastructure:** Docker / Railway / Vercel

## 🔌 API Endpoints
- `POST /webhook (Telegram Update Entry)`
- `GET /health (Health Check)`

## 🚀 Implementation Plan
- [ ] 1. Set up Supabase project and get connection string.
- [ ] 2. Create Telegram Bot via BotFather and get API Token.
- [ ] 3. Deploy FastAPI app to a public URL (Railway/Render).
- [ ] 4. Set Webhook URL via FastAPI on startup.
- [ ] 5. Users register via Bot State Machine.
- [ ] 6. Users click 'Find Match' to query DB for compatible profiles.
