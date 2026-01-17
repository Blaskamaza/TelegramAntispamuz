"""
Cost Tracker — Daily budget control with alerts.

Tracks API costs, enforces daily limits, sends alerts when 80% used.
Opens circuit breaker if budget exceeded.

Usage:
    tracker = CostTracker()
    
    if not tracker.check():
        raise BudgetExceeded("Daily limit reached")
    
    result = vertex_client.generate(...)
    tracker.record(result.tokens_used, model="gemini-2.0-flash")
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger("CostTracker")


# Cost per 1K tokens (Gemini API)
COST_PER_1K = {
    "gemini-2.0-flash": 0.00035,
    "gemini-2.0-pro": 0.0025,
    "gemini-1.5-flash": 0.0001,
    "gemini-1.5-pro": 0.00125,
}


class CostTracker:
    """
    Tracks daily API costs with budget limits and alerts.
    
    Uses local file storage (for Redis-free mode).
    """
    
    def __init__(self):
        self.daily_budget = float(os.getenv("DAILY_BUDGET_USD", "50.0"))
        self.alert_threshold = 0.8  # 80%
        self.today = datetime.utcnow().strftime("%Y-%m-%d")
        self.data_file = Path("data/costs.json")
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Create data file if not exists."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.data_file.write_text("{}", encoding="utf-8")
    
    def _load(self) -> dict:
        """Load cost data."""
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except:
            return {}
    
    def _save(self, data: dict):
        """Save cost data."""
        self.data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def get_spent_today(self) -> float:
        """Get total spent today."""
        data = self._load()
        return data.get(self.today, {}).get("spent", 0.0)
    
    def check(self, estimated_cost: float = 0.01) -> bool:
        """
        Check if we can spend more.
        
        Returns:
            True if OK to spend, False if budget exceeded
        """
        spent = self.get_spent_today()
        
        if spent + estimated_cost > self.daily_budget:
            logger.error(f"Budget exceeded: ${spent:.2f} / ${self.daily_budget}")
            
            # Open circuit breaker
            try:
                from services.circuit_breaker import get_vertex_circuit_breaker
                cb = get_vertex_circuit_breaker()
                cb.record_failure()
                cb.record_failure()
                cb.record_failure()
                cb.record_failure()
                cb.record_failure()  # Force open
            except:
                pass
            
            # Alert
            self._alert(f"[CRITICAL] Budget exceeded: ${spent:.2f} / ${self.daily_budget}")
            return False
        
        return True
    
    def record(self, tokens: int, model: str = "gemini-2.0-flash"):
        """
        Record token usage and cost.
        
        Args:
            tokens: Number of tokens used
            model: Model name for pricing
        """
        cost_per_1k = COST_PER_1K.get(model, 0.00035)
        cost = (tokens / 1000) * cost_per_1k
        
        data = self._load()
        
        if self.today not in data:
            data[self.today] = {"spent": 0.0, "tokens": 0, "requests": 0}
        
        data[self.today]["spent"] += cost
        data[self.today]["tokens"] += tokens
        data[self.today]["requests"] += 1
        
        self._save(data)
        
        # 80% warning
        spent = data[self.today]["spent"]
        if spent / self.daily_budget >= self.alert_threshold:
            self._alert(f"[WARNING] 80% budget used: ${spent:.2f} / ${self.daily_budget}")
        
        logger.info(f"Cost recorded: ${cost:.4f} ({tokens} tokens, {model})")
    
    def _alert(self, message: str):
        """Send alert via Telegram (if configured) or log."""
        logger.warning(message)
        
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_ALERT_CHAT_ID")
        
        if telegram_token and chat_id:
            try:
                import requests
                requests.post(
                    f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                    json={"chat_id": chat_id, "text": message},
                    timeout=5
                )
            except:
                pass
    
    def get_report(self) -> dict:
        """Get cost report for today."""
        data = self._load()
        today_data = data.get(self.today, {})
        
        return {
            "date": self.today,
            "spent": today_data.get("spent", 0.0),
            "budget": self.daily_budget,
            "remaining": self.daily_budget - today_data.get("spent", 0.0),
            "tokens": today_data.get("tokens", 0),
            "requests": today_data.get("requests", 0),
            "percentage": (today_data.get("spent", 0.0) / self.daily_budget * 100) if self.daily_budget > 0 else 0
        }


# Singleton
_tracker: Optional[CostTracker] = None

def get_cost_tracker() -> CostTracker:
    """Get singleton cost tracker."""
    global _tracker
    if _tracker is None:
        _tracker = CostTracker()
    return _tracker


if __name__ == "__main__":
    # Test
    tracker = get_cost_tracker()
    print(f"Budget: ${tracker.daily_budget}")
    print(f"Spent today: ${tracker.get_spent_today():.4f}")
    print(f"Can spend: {tracker.check()}")
    print(f"Report: {json.dumps(tracker.get_report(), indent=2)}")
