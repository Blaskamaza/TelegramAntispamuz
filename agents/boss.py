"""
The Boss — Главный Оркестратор UZ AI Factory.
Управляет агентами: Tech Lead, CMO, QA Lead.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Добавляем корневую директорию в путь, чтобы импортировать агентов
sys.path.append(str(Path(__file__).parent.parent))

from agents.tech_lead import TechLead
from agents.cmo import CMO
from agents.qa_lead import QALead
from agents.cpo import CPO
from agents.sales_head import SalesHead
from config import BASE_DIR

class TheBoss:
    """
    AI Orchestrator.
    Запускает конвейер создания стартапа.
    """
    
    def __init__(self):
        self.cpo = CPO()
        self.tech_lead = TechLead()
        self.cmo = CMO()
        self.sales_head = SalesHead()
        self.qa_lead = QALead()
        self.projects_dir = BASE_DIR / "data" / "projects"

    def run_startup_factory(self, idea: str, context: str = ""):
        """
        Запускает полный цикл производства стартапа.
        """
        print(f"\n👔 The Boss: Starting new project for idea: '{idea}'")
        print("="*60)
        
        # 1. Product Phase (CPO)
        print("\n🧠 PHASE 1: PRODUCT STRATEGY (CPO)")
        prd = self.cpo.create_prd(idea, context)
        
        if "error" in prd:
            print(f"❌ Critical Error in PRD: {prd['error']}")
            return
            
        project_name = prd.get("project_name", "Unknown Project")
        print(f"✅ PRD created for: {project_name}")
        
        # Convert PRD to string for Tech Lead
        prd_str = json.dumps(prd, indent=2)

        # 2. Engineering Phase (Tech Lead)
        print("\n🏗 PHASE 2: ENGINEERING (Tech Lead)")
        tech_spec = self.tech_lead.create_spec(project_name, prd_str) # Pass PRD instead of raw idea
        
        if "error" in tech_spec:
            print(f"❌ Critical Error in Tech Spec: {tech_spec['error']}")
            return
            
        print(f"✅ Tech Spec created.")
        
        # 3. Marketing Phase (CMO)
        print("\n📢 PHASE 3: MARKETING (CMO)")
        # Convert tech spec to string for CMO
        tech_spec_str = json.dumps(tech_spec, indent=2)
        marketing_plan = self.cmo.create_marketing_plan(project_name, tech_spec_str, context)
        
        if "error" in marketing_plan:
            print(f"❌ Critical Error in Marketing Plan: {marketing_plan['error']}")
            return
            
        print(f"✅ Marketing Plan created.")

        # 4. Sales Phase (Sales Head)
        print("\n💰 PHASE 4: SALES AUTOMATION (Sales Head)")
        # Convert marketing plan to string for Sales Head
        marketing_str = json.dumps(marketing_plan, indent=2)
        sales_kit = self.sales_head.create_sales_kit(project_name, marketing_str, context)
        
        if "error" in sales_kit:
            print(f"❌ Critical Error in Sales Kit: {sales_kit['error']}")
            return
            
        print(f"✅ Sales Kit created.")
        
        # 5. Quality Assurance Phase (QA Lead)
        print("\n⚖️ PHASE 5: QUALITY CONTROL (QA Lead)")
        qa_report = self.qa_lead.review_project(project_name)
        
        if "error" in qa_report:
            print(f"❌ Critical Error in QA Report: {qa_report['error']}")
            return
            
        # 6. Final Decision
        print("\n🏁 PHASE 6: FINAL VERDICT")
        status = qa_report.get("status", "UNKNOWN")
        score = qa_report.get("score", 0)
        
        print(f"   Status: {status}")
        print(f"   Score: {score}/100")
        
        if status == "FAIL" or score < 60:
            print("\n❌ PROJECT REJECTED BY QA LEAD.")
            print("   Reason: See qa_report.md for critical issues.")
            print("   Action: Iterate on idea or fix critical bugs.")
        elif status == "WARN":
            print("\n⚠️ PROJECT APPROVED WITH WARNINGS.")
            print("   Action: Fix warnings before launch.")
        else:
            print("\n🚀 PROJECT APPROVED! READY FOR LAUNCH.")
            print(f"   Location: {self.projects_dir}/{project_name.lower().replace(' ', '_')}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Startup Factory")
    parser.add_argument("--idea", type=str, help="Business Idea", required=True)
    parser.add_argument("--context", type=str, help="Market Context", default="Uzbekistan Market")
    
    args = parser.parse_args()
    
    boss = TheBoss()
    boss.run_startup_factory(args.idea, args.context)
