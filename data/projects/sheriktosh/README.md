# SherikTosh - Tashkent Flatmate Finder MVP

## Overview
A mobile-first Telegram bot to help students and young professionals in Tashkent find roommates efficiently.

## Tech Stack
- **Language:** Python 3.11
- **Framework:** FastAPI (Web server) + Aiogram 3 (Bot logic)
- **Database:** PostgreSQL (Async)

## Setup
1. `pip install -r requirements.txt`
2. Create `.env` file with `BOT_TOKEN` and `DATABASE_URL`.
3. Run: `uvicorn src.main:app --reload`
