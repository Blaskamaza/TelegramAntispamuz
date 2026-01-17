"""
Idempotency Store — Prevent duplicate work.

Uses local file storage (Redis-free mode) to track completed operations.
Prevents re-running expensive operations like PRD generation.

Usage:
    store = IdempotencyStore()
    
    key = store.get_key(idea, "cpo")
    if store.check(key, "generate_prd"):
        # Already done, skip
        return cached_result
    
    result = expensive_operation()
    store.record(key, "generate_prd")
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger("Idempotency")


class IdempotencyStore:
    """
    Tracks completed operations to prevent duplicates.
    """
    
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self.data_file = Path("data/idempotency.json")
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Create data file if not exists."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.data_file.write_text("{}", encoding="utf-8")
    
    def _load(self) -> dict:
        """Load idempotency data."""
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except:
            return {}
    
    def _save(self, data: dict):
        """Save idempotency data."""
        self.data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def _cleanup_expired(self, data: dict) -> dict:
        """Remove expired entries."""
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=self.ttl_hours)
        
        cleaned = {}
        for key, value in data.items():
            try:
                recorded_at = datetime.fromisoformat(value.get("recorded_at", ""))
                if recorded_at > cutoff:
                    cleaned[key] = value
            except:
                pass
        
        return cleaned
    
    def get_key(self, task: str, agent: str) -> str:
        """
        Generate unique key from task content and agent.
        
        Args:
            task: Task description/idea
            agent: Agent name
            
        Returns:
            SHA256 hash prefix
        """
        content = f"{task.strip().lower()}:{agent}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def check(self, key: str, operation: str) -> bool:
        """
        Check if operation was already completed.
        
        Args:
            key: Idempotency key (from get_key)
            operation: Operation name (e.g., "generate_prd")
            
        Returns:
            True if already done (skip), False if not done (proceed)
        """
        full_key = f"{key}:{operation}"
        data = self._load()
        data = self._cleanup_expired(data)
        
        if full_key in data:
            logger.info(f"Idempotency hit: {operation} for {key[:8]}...")
            return True
        
        return False
    
    def record(self, key: str, operation: str, result_path: Optional[str] = None):
        """
        Record completed operation.
        
        Args:
            key: Idempotency key
            operation: Operation name
            result_path: Optional path to cached result
        """
        full_key = f"{key}:{operation}"
        data = self._load()
        data = self._cleanup_expired(data)
        
        data[full_key] = {
            "operation": operation,
            "recorded_at": datetime.utcnow().isoformat(),
            "result_path": result_path
        }
        
        self._save(data)
        logger.info(f"Idempotency recorded: {operation} for {key[:8]}...")
    
    def get_cached_result(self, key: str, operation: str) -> Optional[str]:
        """Get cached result path if available."""
        full_key = f"{key}:{operation}"
        data = self._load()
        
        entry = data.get(full_key)
        if entry:
            return entry.get("result_path")
        return None
    
    def invalidate(self, key: str, operation: str):
        """Invalidate (remove) a recorded operation."""
        full_key = f"{key}:{operation}"
        data = self._load()
        
        if full_key in data:
            del data[full_key]
            self._save(data)
            logger.info(f"Idempotency invalidated: {operation} for {key[:8]}...")


# Singleton
_store: Optional[IdempotencyStore] = None

def get_idempotency_store() -> IdempotencyStore:
    """Get singleton idempotency store."""
    global _store
    if _store is None:
        _store = IdempotencyStore()
    return _store


if __name__ == "__main__":
    # Test
    store = get_idempotency_store()
    
    test_key = store.get_key("Food delivery app", "cpo")
    print(f"Key: {test_key}")
    print(f"Already done: {store.check(test_key, 'generate_prd')}")
    
    store.record(test_key, "generate_prd", "worktrees/feat-test/prd.md")
    print(f"After record: {store.check(test_key, 'generate_prd')}")
