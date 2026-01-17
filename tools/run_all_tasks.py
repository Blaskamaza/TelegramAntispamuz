"""
Run All Tasks — Batch execute all pending tasks.

Works with Ralph Loop for continuous execution until completion.

Usage:
    python tools/run_all_tasks.py --parallel=3
    python tools/run_all_tasks.py --wait --timeout=600
"""

import sys
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.workspace_manager import WorkspaceManager
from services.agent_runner import AgentRunner
from config import V2_MAX_PARALLEL_TASKS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("RunAllTasks")


def get_pending_tasks(wm: WorkspaceManager) -> List[Dict]:
    """Get all tasks in backlog status."""
    workspaces = wm.list_workspaces()
    return [
        ws for ws in workspaces
        if ws.get("meta", {}).get("status") == "backlog"
    ]


def run_all_tasks(
    parallel: int = 3,
    wait: bool = True,
    timeout: int = 600,
    agent: str = "cpo"
):
    """
    Run all pending tasks.
    
    Args:
        parallel: Max parallel tasks
        wait: Wait for completion
        timeout: Timeout per task in seconds
        agent: Agent to use
    """
    wm = WorkspaceManager()
    pending = get_pending_tasks(wm)
    
    logger.info("=" * 60)
    logger.info(f"RUN ALL TASKS (parallel={parallel}, wait={wait})")
    logger.info(f"Pending tasks: {len(pending)}")
    logger.info("=" * 60)
    
    if not pending:
        logger.info("No pending tasks")
        return
    
    # Track active runners
    active_runners: Dict[str, AgentRunner] = {}
    completed = 0
    failed = 0
    
    task_queue = [ws.get("task_id") for ws in pending]
    
    while task_queue or active_runners:
        # Start new tasks if we have capacity
        while len(active_runners) < parallel and task_queue:
            task_id = task_queue.pop(0)
            logger.info(f"Starting: {task_id}")
            
            try:
                runner = AgentRunner(task_id, agent)
                runner.start()
                active_runners[task_id] = runner
            except Exception as e:
                logger.error(f"Failed to start {task_id}: {e}")
                failed += 1
        
        if not wait:
            logger.info(f"Started {len(active_runners)} tasks (not waiting)")
            break
        
        # Check for completed tasks
        for task_id in list(active_runners.keys()):
            runner = active_runners[task_id]
            
            if not runner.is_running():
                # Check result
                meta = wm.get_meta(task_id)
                status = meta.get("status", "unknown") if meta else "unknown"
                
                if status == "completed":
                    logger.info(f"Completed: {task_id}")
                    completed += 1
                else:
                    logger.warning(f"Failed: {task_id} (status={status})")
                    failed += 1
                
                del active_runners[task_id]
        
        if active_runners:
            time.sleep(2)  # Poll interval
    
    logger.info("=" * 60)
    logger.info(f"Completed: {completed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Remaining: {len(task_queue)}")
    logger.info("=" * 60)
    
    return {"completed": completed, "failed": failed, "remaining": len(task_queue)}


def ralph_loop_mode(max_iterations: int = 100):
    """
    Ralph Loop mode — continuously process tasks until done.
    
    Runs until:
    - No more pending tasks
    - Max iterations reached
    """
    logger.info("RALPH LOOP MODE ACTIVATED")
    
    wm = WorkspaceManager()
    iteration = 0
    total_completed = 0
    total_failed = 0
    
    while iteration < max_iterations:
        iteration += 1
        logger.info(f"\n=== RALPH ITERATION {iteration}/{max_iterations} ===")
        
        pending = get_pending_tasks(wm)
        
        if not pending:
            logger.info("No more pending tasks. Exiting.")
            break
        
        result = run_all_tasks(parallel=3, wait=True, timeout=300)
        total_completed += result.get("completed", 0)
        total_failed += result.get("failed", 0)
        
        # Auto-merge successful tasks
        logger.info("\nChecking for auto-merge...")
        from tools.auto_merge import run_auto_merge
        run_auto_merge(min_xp=50, dry_run=False)
        
        # Wait before next iteration
        time.sleep(5)
    
    logger.info("\n" + "=" * 60)
    logger.info("RALPH LOOP COMPLETE")
    logger.info(f"Total completed: {total_completed}")
    logger.info(f"Total failed: {total_failed}")
    logger.info(f"Iterations: {iteration}")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all tasks")
    parser.add_argument("--parallel", type=int, default=V2_MAX_PARALLEL_TASKS, 
                       help="Max parallel tasks")
    parser.add_argument("--wait", action="store_true", help="Wait for completion")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per task")
    parser.add_argument("--agent", default="cpo", help="Agent to use")
    parser.add_argument("--ralph", action="store_true", 
                       help="Ralph Loop mode - continuous until done")
    
    args = parser.parse_args()
    
    if args.ralph:
        ralph_loop_mode()
    else:
        run_all_tasks(
            parallel=args.parallel,
            wait=args.wait,
            timeout=args.timeout,
            agent=args.agent
        )
