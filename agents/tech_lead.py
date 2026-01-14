"""
Tech Lead Agent — Главный инженер UZ AI Factory
Отвечает за превращение бизнес-идей в технические спецификации.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from config import (
    GOOGLE_API_KEY, GEMINI_PRO_MODEL, BASE_DIR
)

# Настройка Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

class TechLead:
    """
    AI Agent, который действует как Senior Software Architect.
    Принимает идею -> Выдает Техническое Задание (Spec).
    """
    
    def __init__(self):
        self.model_name = GEMINI_PRO_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        self.system_prompt = """
        You are a pragmatic Senior Tech Lead & Software Architect with 15+ years of experience.
        Your goal is to design robust, scalable, and cost-effective MVP solutions for the Uzbekistan market.
        
        Principles:
        1. **Keep it Simple (KISS):** Don't overengineer. Use proven technologies.
        2. **Speed to Market:** Focus on features essential for an MVP.
        3. **Cost Efficiency:** Prefer open-source and free tiers (Supabase, Vercel, Telegram).
        4. **Mobile First:** Uzbekistan is a mobile-first market (Telegram WebApps, PWA).
        
        Tech Stack Preferences (unless specified otherwise):
        - Backend: Python (FastAPI) or Node.js (Hono/Express)
        - Database: PostgreSQL (Supabase)
        - Frontend: React (Vite) or Telegram Mini App
        - AI: Gemini / OpenAI / Perplexity
        """

    def create_spec(self, idea: str, context: str = "") -> Dict:
        """
        Генерирует полную техническую спецификацию + Код + Диаграммы.
        """
        print(f"👷 Tech Lead: Architecting solution for '{idea[:50]}...'")
        
        prompt = f"""
        {self.system_prompt}
        
        BUSINESS IDEA:
        {idea}
        
        CONTEXT:
        {context}
        
        TASK:
        1. Design the System Architecture (Mermaid C4 or Flowchart).
        2. Design the Database Schema (Mermaid ER Diagram).
        3. WRITE THE ACTUAL CODE for the MVP.
        
        CRITICAL INSTRUCTION:
        DO NOT return a "file_structure" list. You MUST return a "file_contents" dictionary where keys are filenames and values are the ACTUAL CODE.
        Generate at least 3-4 core files (e.g., main.py, models.py, config.py, README.md).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "project_name": "Short_Codename",
            "architecture_type": "Monolith / Microservices",
            "tech_stack": {{ "frontend": "...", "backend": "..." }},
            "mermaid_architecture": "graph TD...",
            "mermaid_erd": "erDiagram...",
            "database_schema": "SQL...",
            "api_endpoints": ["GET /api..."],
            "implementation_steps": ["Step 1..."],
            "file_contents": {{
                "README.md": "# Project Name\n\nDescription...",
                "requirements.txt": "fastapi\nuvicorn\n...",
                "src/main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n...",
                "src/models.py": "from pydantic import BaseModel\n..."
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            # Cleaning JSON
            text = response.text.replace("```json", "").replace("```", "").strip()
            spec = json.loads(text)
            
            # Save artifact & Scaffold
            self._save_spec(spec)
            self._scaffold_project(spec)
            
            return spec
            
        except Exception as e:
            print(f"❌ Tech Lead Error: {e}")
            return {"error": str(e)}

    def _save_spec(self, spec: Dict):
        """Сохраняет спецификацию в Markdown с диаграммами"""
        name = spec.get("project_name", "untitled").lower().replace(" ", "_")
        path = BASE_DIR / "data" / "projects" / name
        path.mkdir(parents=True, exist_ok=True)
        
        with open(path / "tech_spec.md", "w", encoding="utf-8") as f:
            f.write(f"# 🏗 Technical Specification: {spec.get('project_name')}\n\n")
            
            f.write("## 🏛 Architecture\n")
            f.write(f"```mermaid\n{spec.get('mermaid_architecture', '')}\n```\n\n")
            
            f.write("## 💾 Database Schema (ERD)\n")
            f.write(f"```mermaid\n{spec.get('mermaid_erd', '')}\n```\n\n")
            
            f.write("## 🛠 Tech Stack\n")
            for k, v in spec.get("tech_stack", {}).items():
                f.write(f"- **{k.capitalize()}:** {v}\n")
            
            f.write("\n## 🔌 API Endpoints\n")
            for ep in spec.get("api_endpoints", []):
                f.write(f"- `{ep}`\n")
                
            f.write("\n## 🚀 Implementation Plan\n")
            for step in spec.get("implementation_steps", []):
                f.write(f"- [ ] {step}\n")
                
        print(f"✅ Spec saved to {path}/tech_spec.md")

    def _scaffold_project(self, spec: Dict):
        """Создает реальные файлы и папки проекта"""
        name = spec.get("project_name", "untitled").lower().replace(" ", "_")
        base_path = BASE_DIR / "data" / "projects" / name
        
        print(f"🏗 Scaffolding project in {base_path}...")
        
        files = spec.get("file_contents", {})
        for file_path, content in files.items():
            full_path = base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        print(f"✅ Created {len(files)} files.")

if __name__ == "__main__":
    # Test run
    agent = TechLead()
    agent.create_spec(
        idea="Telegram bot for finding flatmates in Tashkent. Users fill profile, bot matches them based on interests and budget.",
        context="High demand for rental housing in Tashkent, students looking for roommates."
    )
