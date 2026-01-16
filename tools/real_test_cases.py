"""
Real Test Cases — Create 5 real-world tasks for battle testing.

Usage:
    python tools/real_test_cases.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.workspace_manager import WorkspaceManager


REAL_TASKS = [
    "EdTech платформа для подготовки к ЕНТ",
    "CRM для узбекских дистрибьюторов",
    "Агрегатор доставки еды в Ташкенте",
    "Финтех для кредитных союзов",
    "IoT для поливных систем в Ферганской долине",
]


def create_real_tasks():
    """Create real test cases for battle testing."""
    wm = WorkspaceManager()
    created = []
    
    print("=" * 60)
    print("🧪 CREATING REAL TEST CASES")
    print("=" * 60)
    
    for i, idea in enumerate(REAL_TASKS, 1):
        # Generate task ID
        task_id = f"battle-{i:03d}"
        
        print(f"\n[{i}/{len(REAL_TASKS)}] {idea}")
        
        try:
            worktree = wm.create(task_id, idea, "cpo")
            created.append(task_id)
            print(f"    ✅ Created: {worktree}")
        except Exception as e:
            print(f"    ❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Created: {len(created)}/{len(REAL_TASKS)}")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Run agents:")
    for task_id in created:
        print(f"     python services/agent_runner.py start {task_id} --agent=cpo")
    print("\n  2. Check report:")
    print("     python tools/battle_report.py")
    
    return created


if __name__ == "__main__":
    create_real_tasks()
