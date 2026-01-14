# TashkentPlumbFix - Uber for Plumbers (MVP)

## Overview
A mobile-first Telegram Mini App connecting Tashkent residents with plumbers.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Auth:** Telegram WebApp Native Auth

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in Supabase/Telegram credentials.
3. Run: `uvicorn src.main:app --reload`
