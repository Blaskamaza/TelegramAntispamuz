"""
New Task CLI — Create new tasks quickly.

Usage:
    python tools/new_task.py "Task title" --agent=cpo
    python tools/new_task.py "MVP Delivery App" --agent=tech_lead --skill=prd-standard-uz
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def generate_task_id(title: str) -> str:
    """Generate task ID from title."""
    import re
    from datetime import datetime
    
    # Slugify title
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:20].strip('-')
    
    # Add timestamp
    ts = datetime.now().strftime("%H%M")
    
    return f"{slug}-{ts}"


def main():
    parser = argparse.ArgumentParser(description="Create new task")
    parser.add_argument("title", help="Task title")
    parser.add_argument("--agent", "-a", default="cpo", help="Agent name")
    parser.add_argument("--skill", "-s", default=None, help="Skill to use")
    parser.add_argument("--id", "-i", default=None, help="Custom task ID")
    
    args = parser.parse_args()
    
    # Generate or use provided ID
    task_id = args.id or generate_task_id(args.title)
    
    print(f"📦 Creating task: {task_id}")
    print(f"   Title: {args.title}")
    print(f"   Agent: {args.agent}")
    if args.skill:
        print(f"   Skill: {args.skill}")
    
    try:
        from services.workspace_manager import WorkspaceManager
        wm = WorkspaceManager()
        worktree = wm.create(task_id, args.title, args.agent, args.skill)
        
        print(f"\n✅ Created: {worktree}")
        print(f"🆔 Task ID: {task_id}")
        print(f"\nNext steps:")
        print(f"  1. cd {worktree}")
        print(f"  2. Run agent or edit files")
        print(f"  3. python tools/review.py {task_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
