# 🏗 Technical Specification: HamxonaToshkent (RoommateTashkent)

**Architecture:** Serverless Modular Monolith

## 🛠 Tech Stack
- **Frontend:** React (Vite) + TailwindCSS + shadcn/ui (Telegram Mini App)
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL (Supabase)
- **Infrastructure:** Vercel (Frontend & Serverless Backend Functions)
- **Bot_interface:** Aiogram (Python) running via Webhook

## 💾 Database Schema
```sql
TABLE users (id UUID PK, telegram_id BIGINT UNIQUE, username TEXT, full_name TEXT, age INT, gender VARCHAR(10), role VARCHAR(10), budget_min INT, budget_max INT, preferred_districts TEXT[], bio TEXT, created_at TIMESTAMPTZ);
TABLE user_habits (user_id UUID FK, habit_tag VARCHAR(50));
TABLE interactions (id UUID PK, actor_id UUID FK, target_id UUID FK, action VARCHAR(10) CHECK (action IN ('like', 'pass')), created_at TIMESTAMPTZ);
TABLE matches (id UUID PK, user_a UUID, user_b UUID, matched_at TIMESTAMPTZ);
```

## 🔌 API Endpoints
- `POST /api/auth/telegram (Validate initData)`
- `GET /api/profile/me (Get current user data)`
- `PUT /api/profile (Update preferences/bio)`
- `GET /api/recommendations (Get list of compatible users)`
- `POST /api/interact (Body: {target_id, action: 'like'|'pass'})`
- `GET /api/matches (List of mutual matches)`

## 🚀 Implementation Plan
- [ ] Step 1: Setup Supabase project and define SQL schema with RLS (Row Level Security).
- [ ] Step 2: Initialize FastAPI backend on Vercel and set up Aiogram webhook for the /start command.
- [ ] Step 3: Develop React Frontend (Mobile View) handling Telegram WebApp.initData for auth.
- [ ] Step 4: Implement basic Profile CRUD and 'District' dropdowns specific to Tashkent.
- [ ] Step 5: Build simple matching logic (SQL query filtering by Budget range AND Gender).
- [ ] Step 6: Deploy to Vercel and link to Telegram Bot Father.
