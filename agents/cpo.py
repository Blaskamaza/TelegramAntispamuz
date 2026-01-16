"""
CPO Agent — Chief Product Officer (V2)

This module re-exports CPOv2 as CPO for backwards compatibility.
V1 code has been moved to legacy/v1 branch.

The CPO agent is now powered by the Skills system and writes to Git worktrees.
"""

# Re-export CPOv2 as CPO for backwards compatibility
from agents.v2.cpo_v2 import CPOv2 as CPO

__all__ = ["CPO"]


# === Entry point for AgentRunner ===
if __name__ == "__main__":
    import os
    import sys
    
    # Fix Windows encoding for emoji output
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    
    task_id = os.environ.get("AGENT_TASK_ID")
    
    if task_id:
        print(f"[CPO] Starting for Task: {task_id}")
        from services.workspace_manager import WorkspaceManager
        
        # Load metadata to get the idea
        wm = WorkspaceManager()
        meta = wm.get_meta(task_id)
        idea = meta.get("title", "Unknown Idea")
        context = "Uzbekistan Market"
        
        # Check for MOCK_MODE
        mock_mode = os.environ.get("MOCK_MODE", "").lower() == "true"
        
        if mock_mode:
            # Create mock PRD without calling API
            print("[CPO] MOCK MODE - Creating mock PRD...")
            from pathlib import Path
            
            worktree = Path(f"worktrees/feat-{task_id}")
            prd_path = worktree / "prd.md"
            prd_path.write_text(f"""# PRD: {idea}

## Problem Statement
Mock PRD generated for testing purposes.

## Target Users  
- Uzbekistan market users

## Core Features
- Feature 1
- Feature 2
- Feature 3

## Success Metrics
- Metric 1
- Metric 2

## Generated
Date: {__import__('datetime').datetime.now().isoformat()}
Mode: MOCK
""", encoding="utf-8")
            
            # Update META
            wm.update_meta(task_id, {"status": "completed", "xp_reward": 50})
            
            print(f"[CPO] Mock PRD saved to: {prd_path}")
            print("[CPO] Execution Complete")
            sys.exit(0)
        else:
            # Real execution
            agent = CPO(task_id=task_id)
            result = agent.execute({"idea": idea, "context": context})
            
            if result.success:
                print("[CPO] Execution Complete")
                sys.exit(0)
            else:
                print(f"[CPO] Failed: {result.error}")
                sys.exit(1)
    else:
        # Interactive test
        print("[CPO] No AGENT_TASK_ID set. Running in test mode.")
        agent = CPO()
        result = agent.execute({"idea": "Test MVP", "context": "Uzbekistan"})
        print(f"Success: {result.success}")
