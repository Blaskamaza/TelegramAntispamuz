# Hamxona - Tashkent Flatmate Finder MVP

## Overview
A Telegram Mini App backend to help students/professionals in Tashkent find roommates.

## Stack
- **Backend:** FastAPI
- **DB:** Supabase (PostgreSQL)
- **Auth:** Telegram Native (initData validation)

## Setup
1. `pip install -r requirements.txt`
2. Set `.env` (DATABASE_URL, BOT_TOKEN)
3. Run: `uvicorn src.main:app --reload`