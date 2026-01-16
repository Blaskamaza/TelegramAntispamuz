"""
Battle Report — Collect metrics from all tasks in workspaces.

Usage:
    python tools/battle_report.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.workspace_manager import WorkspaceManager


def generate_report():
    """Generate battle report from all workspaces."""
    wm = WorkspaceManager()
    workspaces = wm.list_workspaces()
    
    if not workspaces:
        print("No workspaces found.")
        return
    
    # Collect metrics
    total = len(workspaces)
    completed = 0
    failed = 0
    running = 0
    backlog = 0
    
    total_xp = 0
    durations = []
    
    print("=" * 60)
    print("📊 BATTLE REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().isoformat()}")
    print()
    
    for ws in workspaces:
        meta = ws.get("meta", {})
        status = meta.get("status", "unknown")
        xp = meta.get("xp_reward", 0) or 0
        
        if status == "completed":
            completed += 1
        elif status == "failed":
            failed += 1
        elif status == "running":
            running += 1
        elif status == "backlog":
            backlog += 1
        
        total_xp += xp
        
        # Calculate duration if timestamps available
        created = meta.get("created_at")
        updated = meta.get("updated_at")
        if created and updated:
            try:
                start = datetime.fromisoformat(created.replace("Z", "+00:00"))
                end = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                duration = (end - start).total_seconds()
                durations.append(duration)
            except:
                pass
    
    avg_duration = sum(durations) / len(durations) if durations else 0
    success_rate = (completed / total * 100) if total > 0 else 0
    
    report = {
        "total": total,
        "completed": completed,
        "failed": failed,
        "running": running,
        "backlog": backlog,
        "success_rate": f"{success_rate:.1f}%",
        "avg_duration_seconds": round(avg_duration, 1),
        "total_xp": total_xp
    }
    
    # Print report
    print(f"Total Tasks:     {total}")
    print(f"Completed:       {completed} ({success_rate:.1f}%)")
    print(f"Failed:          {failed}")
    print(f"Running:         {running}")
    print(f"Backlog:         {backlog}")
    print()
    print(f"Avg Duration:    {avg_duration:.1f}s ({avg_duration/60:.1f}m)")
    print(f"Total XP:        {total_xp}")
    print()
    print("=" * 60)
    
    # JSON output for parsing
    print("\nJSON:")
    print(json.dumps(report, indent=2))
    
    return report


if __name__ == "__main__":
    generate_report()
