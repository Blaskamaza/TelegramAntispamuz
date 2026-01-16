"""
Review CLI — Review and merge task branches.

Usage:
    python tools/review.py <task_id>         # Review and optionally merge
    python tools/review.py <task_id> --auto  # Auto-approve if score >= 80
    python tools/review.py list              # List pending reviews
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def get_branch_meta(branch: str) -> dict:
    """Get META.yml content from branch."""
    try:
        import yaml
        content = subprocess.check_output(
            ["git", "show", f"{branch}:META.yml"],
            stderr=subprocess.DEVNULL,
            encoding="utf-8"
        )
        return yaml.safe_load(content)
    except:
        return {}


def get_branch_diff(branch: str) -> str:
    """Get diff statistics."""
    try:
        return subprocess.check_output(
            ["git", "diff", f"main..{branch}", "--stat"],
            encoding="utf-8"
        )
    except:
        return "No diff available"


def get_branch_files(branch: str) -> list:
    """Get list of changed files."""
    try:
        output = subprocess.check_output(
            ["git", "diff", f"main..{branch}", "--name-only"],
            encoding="utf-8"
        )
        return [f for f in output.strip().split("\n") if f]
    except:
        return []


def get_pending_reviews() -> list:
    """Get all branches in 'review' status."""
    try:
        from services.workspace_manager import WorkspaceManager
        wm = WorkspaceManager()
        workspaces = wm.list_workspaces()
        return [ws for ws in workspaces if ws.get("status") == "review"]
    except Exception as e:
        print(f"Error: {e}")
        return []


def merge_branch(branch: str, task_id: str) -> bool:
    """Merge branch to main and cleanup."""
    try:
        # Switch to main
        subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
        
        # Merge with no-ff
        subprocess.run(
            ["git", "merge", branch, "--no-ff", "-m", f"Merge {branch}: Task {task_id}"],
            check=True,
            capture_output=True
        )
        
        # Remove worktree
        worktree = Path(f"worktrees/feat-{task_id}")
        if worktree.exists():
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                capture_output=True
            )
        
        # Delete branch
        subprocess.run(
            ["git", "branch", "-d", branch],
            capture_output=True
        )
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Merge failed: {e}")
        return False


def reject_task(task_id: str) -> bool:
    """Mark task as blocked and add rejection note."""
    try:
        from services.workspace_manager import WorkspaceManager
        wm = WorkspaceManager()
        wm.update_meta(task_id, {"status": "blocked"})
        return True
    except Exception as e:
        print(f"❌ Rejection failed: {e}")
        return False


def review_task(task_id: str, auto_approve: bool = False) -> None:
    """Interactive review process."""
    branch = f"feat/{task_id}"
    
    print("\n" + "=" * 60)
    print(f"  📋 TASK REVIEW: {task_id}")
    print("=" * 60)
    
    # Get META
    meta = get_branch_meta(branch)
    if not meta:
        print(f"❌ Branch {branch} not found or no META.yml")
        return
    
    # Display META
    print("\n📄 META.yml:")
    print("-" * 40)
    print(f"  Title:   {meta.get('title', 'N/A')}")
    print(f"  Agent:   {meta.get('agent', 'N/A')}")
    print(f"  Status:  {meta.get('status', 'N/A')}")
    print(f"  Skill:   {meta.get('skill', 'None')}")
    print(f"  XP:      {meta.get('xp_reward', 0)}")
    print(f"  Created: {meta.get('created_at', 'N/A')}")
    
    # Display diff
    print("\n📊 GIT DIFF:")
    print("-" * 40)
    diff = get_branch_diff(branch)
    print(diff if diff.strip() else "  No changes")
    
    # Display files
    files = get_branch_files(branch)
    if files:
        print("\n📁 CHANGED FILES:")
        print("-" * 40)
        for f in files[:10]:  # Limit to 10
            print(f"  • {f}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")
    
    # Auto-approve check
    if auto_approve:
        xp = meta.get('xp_reward', 0)
        if isinstance(xp, int) and xp >= 80:
            print(f"\n✅ AUTO-APPROVED (XP: {xp} >= 80)")
            if merge_branch(branch, task_id):
                print("✅ Merged and cleaned up!")
            return
        else:
            print(f"\n⚠️ Auto-approve skipped (XP: {xp} < 80)")
    
    # Interactive decision
    print("\n" + "=" * 60)
    print("  [A] Approve and Merge")
    print("  [R] Reject (mark as blocked)")
    print("  [S] Skip (do nothing)")
    print("=" * 60)
    
    try:
        choice = input("\nYour choice [A/R/S]: ").strip().upper()
    except KeyboardInterrupt:
        print("\n⏭️ Skipped")
        return
    
    if choice == "A":
        print("\n⏳ Merging...")
        if merge_branch(branch, task_id):
            print("✅ Merged and cleaned up!")
            print(f"🎉 Task {task_id} completed!")
        else:
            print("❌ Merge failed. Check for conflicts.")
    
    elif choice == "R":
        print("\n⏳ Rejecting...")
        if reject_task(task_id):
            print("🚫 Task marked as blocked")
        else:
            print("❌ Failed to update status")
    
    else:
        print("⏭️ Skipped")


def list_pending() -> None:
    """List all tasks pending review."""
    pending = get_pending_reviews()
    
    print("\n📋 PENDING REVIEWS:")
    print("-" * 60)
    
    if not pending:
        print("  No tasks in 'review' status")
        return
    
    for ws in pending:
        print(f"  • {ws.get('task_id')}: {ws.get('title')}")
        print(f"    Agent: {ws.get('agent')} | XP: {ws.get('xp_reward', 0)}")
    
    print("-" * 60)
    print(f"  Total: {len(pending)} tasks pending review")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_pending()
    
    elif command == "--help" or command == "-h":
        print(__doc__)
    
    else:
        task_id = command
        auto = "--auto" in sys.argv or "-a" in sys.argv
        review_task(task_id, auto_approve=auto)


if __name__ == "__main__":
    main()
