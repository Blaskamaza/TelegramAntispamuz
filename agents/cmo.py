"""
CMO Agent — Директор по маркетингу UZ AI Factory
Отвечает за стратегию продвижения, контент-план и генерацию постов.
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

class CMO:
    """
    AI Agent, который действует как World-Class Growth Hacker & CMO.
    Принимает Tech Spec -> Выдает Маркетинговую Стратегию и Контент.
    """
    
    def __init__(self):
        self.model_name = GEMINI_PRO_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        self.system_prompt = """
        You are a world-class CMO & Growth Hacker with experience in launching startups in the CIS market (Uzbekistan, Russia, Kazakhstan).
        Your goal is to create a go-to-market strategy that costs $0 (organic growth) but delivers viral results.
        
        Principles:
        1. **Content is King:** Focus on storytelling, not just selling.
        2. **Telegram First:** Uzbekistan is Telegram-centric. Strategy must revolve around channels/bots.
        3. **Viral Loops:** Build mechanisms where users invite others.
        4. **Local Context:** Use local memes, cultural references, and language nuances (Uzbek/Russian).
        """

    def create_marketing_plan(self, project_name: str, tech_spec: str, context: str = "") -> Dict:
        """
        Генерирует полную маркетинговую стратегию и контент-план.
        """
        print(f"📢 CMO: Crafting strategy for '{project_name}'...")
        
        prompt = f"""
        {self.system_prompt}
        
        PROJECT NAME: {project_name}
        
        TECHNICAL SPECIFICATION:
        {tech_spec}
        
        MARKET CONTEXT:
        {context}
        
        TASK:
        1. Define the Target Audience (Avatar).
        2. Create a Unique Value Proposition (UVP).
        3. Develop a "Zero-Budget" Launch Strategy.
        4. Create a 1-Week Content Plan for Telegram.
        5. Write the actual text for the first 3 posts (Launch, Educational, Viral).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "strategy": {{
                "target_audience": "...",
                "uvp": "...",
                "channels": ["Telegram", "Instagram", ...],
                "viral_mechanics": "..."
            }},
            "content_plan": [
                {{ "day": 1, "topic": "...", "format": "Post/Reel/Poll" }},
                ...
            ],
            "posts": [
                {{
                    "type": "Launch Post",
                    "text": "🔥 We are live! ...",
                    "image_prompt": "A futuristic 3D render of..."
                }},
                {{
                    "type": "Educational",
                    "text": "Did you know? ...",
                    "image_prompt": "Infographic showing..."
                }}
            ]
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
            self._save_plan(project_name, data)
            
            return data
            
        except Exception as e:
            print(f"❌ CMO Error: {e}")
            return {"error": str(e)}

    def _save_plan(self, project_name: str, data: Dict):
        """Сохраняет план в Markdown"""
        name = project_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        path = BASE_DIR / "data" / "projects" / name
        path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        with open(path / "marketing_plan.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Save Markdown
        with open(path / "marketing_strategy.md", "w", encoding="utf-8") as f:
            f.write(f"# 📢 Marketing Strategy: {project_name}\n\n")
            
            strat = data.get("strategy", {})
            f.write(f"## 🎯 Target Audience\n{strat.get('target_audience')}\n\n")
            f.write(f"## 💎 UVP\n{strat.get('uvp')}\n\n")
            f.write(f"## 🚀 Launch Strategy\n{strat.get('viral_mechanics')}\n\n")
            
            f.write("## 📅 1-Week Content Plan\n")
            for item in data.get("content_plan", []):
                f.write(f"- **Day {item.get('day')}:** {item.get('topic')} ({item.get('format')})\n")
            
            f.write("\n## 📝 Ready-to-Publish Posts\n")
            for post in data.get("posts", []):
                f.write(f"### {post.get('type')}\n")
                f.write(f"**Text:**\n\n{post.get('text')}\n\n")
                f.write(f"**🎨 Image Prompt:** `{post.get('image_prompt')}`\n\n")
                f.write("---\n")
                
        print(f"✅ Marketing Plan saved to {path}/marketing_strategy.md")

if __name__ == "__main__":
    # Test run
    agent = CMO()
    
    # Load Tech Spec if exists
    project_dir = BASE_DIR / "data" / "projects" / "hamxona_tashkent_flatmate_finder"
    tech_spec_path = project_dir / "tech_spec.md"
    
    tech_spec_content = "A Telegram bot for finding roommates in Tashkent."
    if tech_spec_path.exists():
        with open(tech_spec_path, "r", encoding="utf-8") as f:
            tech_spec_content = f.read()
            
    agent.create_marketing_plan(
        project_name="Hamxona (Tashkent Flatmate Finder)",
        tech_spec=tech_spec_content,
        context="High demand for rental housing, students looking for roommates."
    )
