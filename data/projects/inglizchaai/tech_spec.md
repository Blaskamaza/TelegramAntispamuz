# 🏗 Technical Specification: InglizchaAI

## 🏛 Architecture
```mermaid
graph TD
    User((Student)) -- Voice/Text --> TG[Telegram Cloud]
    TG -- Webhook --> API[FastAPI Gateway]
    subgraph Backend [InglizchaAI Core]
        API --> Router{Router}
        Router -- /webhook --> Bot[Aiogram Bot Logic]
        Router -- /payment --> Pay[Payment Handler]
        Bot -- Audio Bytes --> AI[AI Engine]
        Bot -- User Data --> DB[(Supabase PG)]
    end
    subgraph External Services
        AI -- STT/TTS/LLM --> OpenAI[OpenAI API]
        Pay -- Callback --> Click[Click/Payme API]
    end
```

## 💾 Database Schema (ERD)
```mermaid
erDiagram
    USERS {
        bigint telegram_id PK
        string full_name
        string username
        int xp_points
        boolean is_premium
        timestamp created_at
    }
    SUBSCRIPTIONS {
        uuid id PK
        bigint user_id FK
        string status
        timestamp start_date
        timestamp end_date
    }
    LEARNING_LOGS {
        uuid id PK
        bigint user_id FK
        string user_text
        string corrected_text
        string ai_response
        timestamp created_at
    }
    USERS ||--o{ SUBSCRIPTIONS : has
    USERS ||--o{ LEARNING_LOGS : generates
```

## 🛠 Tech Stack
- **Frontend:** Telegram Mobile App (Bot API)
- **Backend:** Python 3.11 (FastAPI + Aiogram 3.x)
- **Database:** PostgreSQL (Supabase)
- **Ai_engine:** OpenAI (Whisper for STT, GPT-4o-mini for Logic, TTS-1 for Voice)
- **Deployment:** Docker / Vercel / Railway

## 🔌 API Endpoints
- `POST /api/webhook/telegram (Receives updates from Telegram)`
- `POST /api/webhook/click (Receives payment success from Click)`
- `POST /api/webhook/payme (Receives payment success from Payme)`

## 🚀 Implementation Plan
- [ ] 1. Initialize Supabase project and apply SQL schema.
- [ ] 2. Set up Telegram Bot via BotFather and get API Token.
- [ ] 3. Configure OpenAI API keys.
- [ ] 4. Deploy FastAPI backend (src/main.py) to a server/cloud.
- [ ] 5. Set Telegram Webhook to point to the deployed URL.
