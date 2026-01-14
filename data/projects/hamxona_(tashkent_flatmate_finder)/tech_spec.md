# 🏗 Technical Specification: Hamxona (Tashkent Flatmate Finder)

## 🏛 Architecture
```mermaid
graph TD
    User((User))
    TG[Telegram Client]
    TMA[Mini App UI]
    API[FastAPI Backend]
    DB[(Supabase PostgreSQL)]
    Auth[Telegram Auth Validator]

    User --> TG
    TG -->|Opens| TMA
    TG -->|/start command| API
    TMA -->|HTTPS/JSON| API
    API -->|Validate initData| Auth
    API -->|Read/Write| DB
```

## 💾 Database Schema (ERD)
```mermaid
erDiagram
    USERS {
        bigint telegram_id PK
        string username
        string full_name
        int age
        string gender
        int budget_min
        int budget_max
        string district_pref
        jsonb habits
        boolean is_searching
        timestamp created_at
    }
    MATCHES {
        uuid id PK
        bigint user_id_a FK
        bigint user_id_b FK
        string status
    }
    USERS ||--o{ MATCHES : initiates
```

## 🛠 Tech Stack
- **Frontend:** Telegram Mini App (React + Vite + ShadcnUI)
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL (Supabase)
- **Infrastructure:** Docker / Railway or Render (PaaS)

## 🔌 API Endpoints
- `POST /api/v1/auth/login (Validate Telegram WebApp Data)`
- `GET /api/v1/users/me (Get Profile)`
- `PUT /api/v1/users/me (Update Profile)`
- `GET /api/v1/matches/candidates (Find potential flatmates)`
- `POST /api/v1/matches/connect (Send request to user)`

## 🚀 Implementation Plan
- [ ] 1. Setup Supabase project and apply SQL schema.
- [ ] 2. Initialize FastAPI project with SQLModel.
- [ ] 3. Implement Telegram 'initData' validation for stateless auth.
- [ ] 4. Create User CRUD and Profile update endpoints.
- [ ] 5. Implement basic matching logic (Budget overlap + Location).
- [ ] 6. Deploy to Render/Railway.
- [ ] 7. Create Telegram Bot via BotFather and link WebApp URL.
