"""
Sales Head Agent — Автоматизатор Продаж UZ AI Factory
Отвечает за конверсию: Email-рассылки, Тексты лендингов, Воронки в ботах.
НИКАКИХ ЗВОНКОВ. Только автоматические продажи.
"""

import json
import os
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

class SalesHead:
    """
    AI Agent, который действует как Expert Copywriter & Funnel Architect.
    Принимает Marketing Strategy -> Выдает Sales Assets (Emails, Landing Copy, Bot Logic).
    """
    
    def __init__(self):
        self.model_name = GEMINI_PRO_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        self.system_prompt = """
        You are a world-class Digital Sales Architect & Direct Response Copywriter.
        Your goal is to build **Fully Automated Sales Systems** for startups in Uzbekistan.
        
        Constraints:
        1. **NO HUMAN CALLS:** The user has NO employees. Everything must be automated (Bots, Emails, Ads).
        2. **High Conversion:** Use frameworks like AIDA, PAS (Problem-Agitation-Solution).
        3. **Trust Building:** Since there are no humans, the copy must build extreme trust instantly.
        4. **Local Context:** Uzbekistan market loves "Bonuses", "Discounts", and "Social Proof".
        """

    def create_sales_kit(self, project_name: str, marketing_strategy: str, context: str = "") -> Dict:
        """
        Генерирует набор активов для автоматических продаж.
        """
        print(f"💰 Sales Head: Building automated funnel for '{project_name}'...")
        
        prompt = f"""
        {self.system_prompt}
        
        PROJECT NAME: {project_name}
        
        MARKETING STRATEGY:
        {marketing_strategy}
        
        MARKET CONTEXT:
        {context}
        
        TASK:
        Create a "Zero-Human" Sales Kit.
        
        1. **Landing Page Copy (Hero Section + UVP):** The exact text for the main website/bot start message.
        2. **Cold Outreach Email/DM:** A high-converting message to send to potential partners/users (automated).
        3. **Telegram Bot Sales Flow:** A logic tree for the bot to sell the product without a human.
        4. **Lead Magnet Idea:** Something free to give away in exchange for a subscription.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "landing_page": {{
                "headline": "...",
                "subheadline": "...",
                "cta_button": "..."
            }},
            "outreach_message": {{
                "subject": "...",
                "body": "..."
            }},
            "bot_flow": [
                {{ "step": 1, "message": "Welcome!...", "buttons": ["Buy", "Learn More"] }},
                {{ "step": 2, "trigger": "Learn More", "message": "Here is why..." }}
            ],
            "lead_magnet": {{
                "title": "...",
                "description": "..."
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
            data = json.loads(text)
            
            # Save artifact
            self._save_kit(project_name, data)
            
            return data
            
        except Exception as e:
            print(f"❌ Sales Head Error: {e}")
            return {"error": str(e)}

    def _save_kit(self, project_name: str, data: Dict):
        """Сохраняет Sales Kit в Markdown"""
        # Normalize name to match Tech Lead's folder naming
        folder_name = project_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        path = BASE_DIR / "data" / "projects" / folder_name
        path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        with open(path / "sales_kit.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Save Markdown
        with open(path / "sales_kit.md", "w", encoding="utf-8") as f:
            f.write(f"# 💰 Automated Sales Kit: {project_name}\n\n")
            
            # Lead Magnet
            lm = data.get("lead_magnet", {})
            f.write(f"## 🧲 Lead Magnet\n")
            f.write(f"**Title:** {lm.get('title')}\n")
            f.write(f"**Description:** {lm.get('description')}\n\n")
            
            # Landing Page
            lp = data.get("landing_page", {})
            f.write(f"## 🌐 Landing Page Copy\n")
            f.write(f"# {lp.get('headline')}\n")
            f.write(f"### {lp.get('subheadline')}\n")
            f.write(f"**[ {lp.get('cta_button')} ]**\n\n")
            
            # Outreach
            out = data.get("outreach_message", {})
            f.write(f"## 📧 Automated Outreach (Email/DM)\n")
            f.write(f"**Subject:** {out.get('subject')}\n")
            f.write(f"**Body:**\n{out.get('body')}\n\n")
            
            # Bot Flow
            f.write(f"## 🤖 Telegram Bot Sales Flow\n")
            for step in data.get("bot_flow", []):
                f.write(f"**Step {step.get('step')}:** {step.get('message')}\n")
                if "buttons" in step:
                    f.write(f"*Buttons:* {step.get('buttons')}\n")
                if "trigger" in step:
                    f.write(f"*Trigger:* User clicks '{step.get('trigger')}'\n")
                f.write("\n")
                
        print(f"✅ Sales Kit saved to {path}/sales_kit.md")

if __name__ == "__main__":
    # Test run
    agent = SalesHead()
    
    # Try to load Marketing Strategy from Hamxona
    project_name = "Hamxona (Tashkent Flatmate Finder)"
    folder_name = "hamxona_tashkent_flatmate_finder"
    strategy_path = BASE_DIR / "data" / "projects" / folder_name / "marketing_strategy.md"
    
    strategy_content = "Target Audience: Students. UVP: No commission."
    if strategy_path.exists():
        with open(strategy_path, "r", encoding="utf-8") as f:
            strategy_content = f.read()
            
    agent.create_sales_kit(
        project_name=project_name,
        marketing_strategy=strategy_content,
        context="Uzbekistan, Telegram-first market."
    )
