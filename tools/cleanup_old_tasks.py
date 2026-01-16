"""
Cleanup Old Tasks — Remove old completed/failed tasks.

Run via cron every 6 hours:
    0 */6 * * * python tools/cleanup_old_tasks.py

Usage:
    python tools/cleanup_old_tasks.py [--dry-run] [--max-age-days=7]
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.workspace_manager import WorkspaceManager


def cleanup(max_age_days: int = 7, dry_run: bool = False):
    """Remove old completed/failed tasks."""
    wm = WorkspaceManager()
    workspaces = wm.list_workspaces()
    
    now = datetime.now()
    removed = 0
    skipped = 0
    
    print("=" * 60)
    print(f"🧹 CLEANUP OLD TASKS (max age: {max_age_days} days)")
    print("=" * 60)
    
    for ws in workspaces:
        meta = ws.get("meta", {})
        task_id = ws.get("task_id", "unknown")
        status = meta.get("status", "unknown")
        
        # Only clean completed/failed tasks
        if status not in ["completed", "failed"]:
            skipped += 1
            continue
        
        # Check age
        created_str = meta.get("created_at")
        if not created_str:
            skipped += 1
            continue
        
        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            age = now - created.replace(tzinfo=None)
            
            if age.days > max_age_days:
                if dry_run:
                    print(f"  [DRY RUN] Would remove: {task_id} (age: {age.days} days)")
                else:
                    wm.remove(task_id, force=True)
                    print(f"  ✅ Removed: {task_id} (age: {age.days} days)")
                removed += 1
            else:
                skipped += 1
                
        except Exception as e:
            print(f"  ❌ Error processing {task_id}: {e}")
            skipped += 1
    
    print()
    print("=" * 60)
    print(f"Removed: {removed}")
    print(f"Skipped: {skipped}")
    if dry_run:
        print("[DRY RUN MODE - no changes made]")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup old tasks")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually remove")
    parser.add_argument("--max-age-days", type=int, default=7, help="Max age in days")
    
    args = parser.parse_args()
    cleanup(max_age_days=args.max_age_days, dry_run=args.dry_run)
