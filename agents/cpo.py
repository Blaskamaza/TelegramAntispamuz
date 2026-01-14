"""
CPO Agent — Директор по продукту UZ AI Factory
Отвечает за превращение "идеи" в "продукт". Пишет PRD (Product Requirements Document).
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

class CPO:
    """
    AI Agent, который действует как Senior Product Manager.
    Принимает Raw Idea -> Выдает PRD (User Stories, Features, Monetization).
    """
    
    def __init__(self):
        self.model_name = GEMINI_PRO_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        self.system_prompt = """
        You are a visionary Chief Product Officer (CPO) for a startup factory in Uzbekistan.
        Your goal is to take a vague business idea and turn it into a concrete Product Requirements Document (PRD).
        
        Principles:
        1. **User First:** Focus on the problem and the user, not just features.
        2. **MVP Mindset:** Define what is critical for V1 vs what can wait.
        3. **Monetization:** The product must make money. Define how.
        4. **Local Context:** Adapt features for the Uzbekistan market (Telegram, P2P transfers, trust issues).
        """

    def create_prd(self, idea: str, context: str = "") -> Dict:
        """
        Генерирует PRD (Product Requirements Document).
        """
        print(f"🧠 CPO: Analyzing idea '{idea}'...")
        
        prompt = f"""
        {self.system_prompt}
        
        IDEA: {idea}
        
        MARKET CONTEXT:
        {context}
        
        TASK:
        Create a comprehensive PRD.
        
        1. **Problem Statement:** What pain are we solving?
        2. **Target Audience:** Who are the users? (Personas)
        3. **User Stories:** "As a [user], I want to [action], so that [benefit]."
        4. **Core Features (MVP):** List the absolute must-haves.
        5. **Monetization Strategy:** How do we make money? (Subscription, Commission, Ads).
        6. **Success Metrics:** Key KPIs (e.g., DAU, Retention).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "project_name": "Short Catchy Name",
            "problem": "...",
            "audience": ["Student", "Landlord"],
            "user_stories": [
                "As a student, I want to filter by price...",
                "As a landlord, I want to hide my phone number..."
            ],
            "features": {{
                "mvp": ["Search", "Chat", "Payment"],
                "future": ["AI Matching", "Map View"]
            }},
            "monetization": "Freemium model...",
            "metrics": ["1000 users in month 1", "5% conversion"]
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
            self._save_prd(data)
            
            return data
            
        except Exception as e:
            print(f"❌ CPO Error: {e}")
            return {"error": str(e)}

    def _save_prd(self, data: Dict):
        """Сохраняет PRD в Markdown"""
        project_name = data.get("project_name", "Unknown Project")
        folder_name = project_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        path = BASE_DIR / "data" / "projects" / folder_name
        path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        with open(path / "prd.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Save Markdown
        with open(path / "prd.md", "w", encoding="utf-8") as f:
            f.write(f"# 🧠 Product Requirements Document (PRD): {project_name}\n\n")
            
            f.write(f"## 🚩 Problem Statement\n{data.get('problem')}\n\n")
            
            f.write("## 👥 Target Audience\n")
            for persona in data.get("audience", []):
                f.write(f"- {persona}\n")
            f.write("\n")
            
            f.write("## 📖 User Stories\n")
            for story in data.get("user_stories", []):
                f.write(f"- {story}\n")
            f.write("\n")
            
            f.write("## 🛠 Core Features (MVP)\n")
            for feature in data.get("features", {}).get("mvp", []):
                f.write(f"- [ ] {feature}\n")
            f.write("\n")
            
            f.write("## 🔮 Future Features\n")
            for feature in data.get("features", {}).get("future", []):
                f.write(f"- {feature}\n")
            f.write("\n")
            
            f.write(f"## 💰 Monetization\n{data.get('monetization')}\n\n")
            
            f.write("## 📈 Success Metrics\n")
            for metric in data.get("metrics", []):
                f.write(f"- {metric}\n")
                
        print(f"✅ PRD saved to {path}/prd.md")

if __name__ == "__main__":
    # Test run
    agent = CPO()
    agent.create_prd(
        idea="A marketplace for renting wedding dresses in Tashkent.",
        context="Weddings are huge in Uzbekistan, but dresses are expensive to buy."
    )
