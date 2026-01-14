"""
QA Lead Agent — Директор по качеству UZ AI Factory
Отвечает за критику, проверку безопасности и поиск галлюцинаций.
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

class QALead:
    """
    AI Agent, который действует как Senior QA Engineer & Security Auditor.
    Принимает Artifacts (Spec, Plan) -> Выдает Report (Pass/Fail + Issues).
    """
    
    def __init__(self):
        self.model_name = GEMINI_PRO_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        self.system_prompt = """
        You are a cynical, detail-oriented Senior QA Lead & Security Auditor.
        Your goal is to find flaws, security risks, hallucinations, and logic errors in AI-generated content.
        
        Principles:
        1. **Trust No One:** AI agents hallucinate. Verify everything.
        2. **Security First:** Look for SQL injection risks, exposed APIs, and weak auth.
        3. **Cultural Safety:** Ensure content is appropriate for Uzbekistan (conservative, family-oriented).
        4. **Logic Check:** Does the business model actually make sense?
        """

    def review_project(self, project_name: str) -> Dict:
        """
        Проводит полный аудит проекта (Tech Spec + Marketing Plan).
        """
        print(f"🧐 QA Lead: Auditing '{project_name}'...")
        
        # Load Artifacts
        # Normalize name to match Tech Lead's folder naming (lowercase, spaces to underscores, remove parens)
        folder_name = project_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        project_dir = BASE_DIR / "data" / "projects" / folder_name
        
        print(f"   📂 Looking in: {project_dir}")
        
        tech_spec = self._load_file(project_dir / "tech_spec.md")
        marketing_plan = self._load_file(project_dir / "marketing_strategy.md")
        
        if not tech_spec and not marketing_plan:
            return {"error": "No artifacts found to review."}
            
        prompt = f"""
        {self.system_prompt}
        
        PROJECT: {project_name}
        
        ARTIFACT 1: TECHNICAL SPECIFICATION
        {tech_spec[:10000]} ... (truncated)
        
        ARTIFACT 2: MARKETING STRATEGY
        {marketing_plan[:10000]} ... (truncated)
        
        TASK:
        Perform a comprehensive audit.
        
        1. **Tech Review:** Check for architecture flaws, security risks (OWASP Top 10), and missing components.
        2. **Marketing Review:** Check for hallucinations (promising features that don't exist), cultural insensitivity, or scammy vibes.
        3. **Consistency Check:** Does the Marketing Plan match the Tech Spec? (e.g., Marketing promises an App, Spec builds a Bot).
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "status": "PASS / FAIL / WARN",
            "score": 85,
            "critical_issues": [
                "Security: User ID exposed in API...",
                "Logic: Marketing promises AI Video, but Tech Spec only has Text..."
            ],
            "warnings": [
                "UX: Too many steps to register..."
            ],
            "suggestions": [
                "Add Rate Limiting to API...",
                "Change tone of post #2..."
            ],
            "final_verdict": "Ready for MVP but fix security issues first."
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
            report = json.loads(text)
            
            # Save artifact
            self._save_report(project_dir, report)
            
            return report
            
        except Exception as e:
            print(f"❌ QA Lead Error: {e}")
            return {"error": str(e)}

    def _load_file(self, path: Path) -> str:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _save_report(self, project_dir: Path, report: Dict):
        """Сохраняет отчет в Markdown"""
        with open(project_dir / "qa_report.md", "w", encoding="utf-8") as f:
            status_emoji = "✅" if report.get("status") == "PASS" else "❌" if report.get("status") == "FAIL" else "⚠️"
            
            f.write(f"# {status_emoji} QA Report: {report.get('status')} (Score: {report.get('score')})\n\n")
            f.write(f"**Verdict:** {report.get('final_verdict')}\n\n")
            
            f.write("## 🚨 Critical Issues\n")
            for issue in report.get("critical_issues", []):
                f.write(f"- 🔴 {issue}\n")
                
            f.write("\n## ⚠️ Warnings\n")
            for warn in report.get("warnings", []):
                f.write(f"- 🟠 {warn}\n")
                
            f.write("\n## 💡 Suggestions\n")
            for sugg in report.get("suggestions", []):
                f.write(f"- 🔵 {sugg}\n")
                
        print(f"✅ QA Report saved to {project_dir}/qa_report.md")

if __name__ == "__main__":
    # Test run
    agent = QALead()
    agent.review_project("Hamxona (Tashkent Flatmate Finder)")
