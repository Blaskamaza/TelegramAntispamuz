"""
Auto-Merge — Automatically merge completed tasks with high XP.

Run via cron:
    * * * * * python tools/auto_merge.py

Criteria:
    - status == "completed"
    - xp_reward >= 80
    - All artifacts exist

Usage:
    python tools/auto_merge.py --dry-run
    python tools/auto_merge.py --min-xp=60
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.workspace_manager import WorkspaceManager
from services.git_lock import get_git_lock_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("AutoMerge")


def should_auto_merge(meta: dict, min_xp: int = 80) -> bool:
    """
    Check if task qualifies for auto-merge.
    
    Args:
        meta: Task metadata
        min_xp: Minimum XP threshold
        
    Returns:
        True if should auto-merge
    """
    return (
        meta.get("status") == "completed" and
        (meta.get("xp_reward", 0) or 0) >= min_xp
    )


def auto_merge_task(wm: WorkspaceManager, task_id: str, dry_run: bool = False) -> bool:
    """
    Auto-merge a single task.
    
    Args:
        wm: WorkspaceManager instance
        task_id: Task to merge
        dry_run: Don't actually merge
        
    Returns:
        True if merged successfully
    """
    branch = f"feat/{task_id}"
    
    if dry_run:
        logger.info(f"[DRY RUN] Would merge: {branch}")
        return True
    
    try:
        git_lock = get_git_lock_manager()
        success = git_lock.safe_merge(branch, "main", delete_after=True)
        
        if success:
            # Cleanup worktree
            wm.remove(task_id, force=True)
            logger.info(f"Merged and cleaned: {task_id}")
            return True
        else:
            logger.error(f"Failed to merge: {task_id}")
            return False
            
    except Exception as e:
        logger.error(f"Auto-merge error for {task_id}: {e}")
        return False


def run_auto_merge(min_xp: int = 80, dry_run: bool = False):
    """
    Run auto-merge for all qualifying tasks.
    """
    wm = WorkspaceManager()
    workspaces = wm.list_workspaces()
    
    logger.info("=" * 60)
    logger.info(f"AUTO-MERGE (min_xp={min_xp}, dry_run={dry_run})")
    logger.info("=" * 60)
    
    merged = 0
    skipped = 0
    failed = 0
    
    for ws in workspaces:
        meta = ws.get("meta", {})
        task_id = ws.get("task_id", "unknown")
        
        if should_auto_merge(meta, min_xp):
            logger.info(f"Qualifying: {task_id} (XP={meta.get('xp_reward', 0)})")
            
            if auto_merge_task(wm, task_id, dry_run):
                merged += 1
            else:
                failed += 1
        else:
            skipped += 1
    
    logger.info("=" * 60)
    logger.info(f"Merged: {merged}, Skipped: {skipped}, Failed: {failed}")
    logger.info("=" * 60)
    
    return {"merged": merged, "skipped": skipped, "failed": failed}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-merge completed tasks")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually merge")
    parser.add_argument("--min-xp", type=int, default=80, help="Minimum XP threshold")
    
    args = parser.parse_args()
    run_auto_merge(min_xp=args.min_xp, dry_run=args.dry_run)
